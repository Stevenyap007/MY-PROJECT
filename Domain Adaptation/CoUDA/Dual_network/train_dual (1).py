import os
import glob
import tensorflow as tf
import numpy as np
from tensorflow.keras import layers, Model
from tensorflow.keras.applications import MobileNetV2
from sklearn.utils.class_weight import compute_class_weight
import tensorflow.keras.backend as K
from tensorflow.keras import regularizers

# Disable XLA JIT
os.environ["TF_XLA_FLAGS"] = "--tf_xla_auto_jit=0"

# Disable cuDNN exhaustive search
tf.config.experimental.enable_cudnn_auto_tune = False


# ----------------------------------------------------------
# ---- Gradient Reversal Layer ----
# ----------------------------------------------------------
class GradientReversal(tf.keras.layers.Layer):
    def __init__(self, hp_lambda=1.0, **kwargs):
        super().__init__(**kwargs)
        self.hp_lambda = hp_lambda

    def call(self, x):
        # Forward pass is identity
        @tf.custom_gradient
        def _reverse(x):
            def grad(dy):
                return -self.hp_lambda * dy  # flip gradient sign
            return x, grad
        return _reverse(x)


# ----------------------------------------------------------
# Domain discriminator
# ----------------------------------------------------------
def make_domain_discriminator(input_shape=(1280,), hidden=256):
    inp = layers.Input(shape=input_shape)
    x = layers.Dense(hidden, activation="relu")(inp)
    x = layers.Dense(hidden, activation="relu")(x)
    out = layers.Dense(1, activation="sigmoid")(x)  # domain prob (source=1, target=0)
    return Model(inp, out, name="domain_discriminator")

# ----------------------------------------------------------
# Noise co-adaptation layer
# ----------------------------------------------------------
class NoiseCoAdapt(tf.keras.layers.Layer):
    """
    Implements a noise transition mapping p(z|y=k, f) parameterized per (k,m)
    We follow the paper: softmax over m for each true class k conditioned on f.
    """
    def __init__(self, num_classes, hidden_dim=128, **kwargs):
        super().__init__(**kwargs)
        self.num_classes = num_classes
        self.hidden_dim = hidden_dim
        # we map features -> (K x K) logits, implemented by mapping features to K*H then to K*K
        self.dense1 = layers.Dense(hidden_dim, activation="relu")
        self.dense2 = layers.Dense(num_classes * num_classes)  # flattened KxK logits

    def call(self, features, pred_probs):
        # features: [B, F], pred_probs: [B, K] (softmax)
        h = self.dense1(features)                     # [B, H]
        logits = self.dense2(h)                       # [B, K*K]
        logits = tf.reshape(logits, (-1, self.num_classes, self.num_classes))  # [B, K, K]
        # softmax over m (noisy class) dimension for each true class k:
        p_z_given_yf = tf.nn.softmax(logits, axis=-1)  # [B, K, K]
        # predicted noisy distribution p(z=m|x,f) = sum_k p(z|y=k,f) * p(y=k|x)
        pz = tf.einsum('bkm,bk->bm', p_z_given_yf, pred_probs)  # [B, K]
        return pz, p_z_given_yf
    

# ----------------------------------------------------------
# MMD loss
# ----------------------------------------------------------
def gaussian_kernel_matrix(x, y, sigmas):
    beta = 1. / (2. * (tf.reshape(sigmas, (-1, 1))))
    dist = _pairwise_sq_dists(x, y)
    s = tf.matmul(beta, tf.reshape(dist, (1, -1)))
    return tf.reduce_sum(tf.exp(-s), axis=0)

def _pairwise_sq_dists(x, y):
    # x: [n, d], y: [m, d]
    normx = tf.reduce_sum(tf.square(x), axis=1, keepdims=True)
    normy = tf.reduce_sum(tf.square(y), axis=1, keepdims=True)
    return normx - 2.0 * tf.matmul(x, y, transpose_b=True) + tf.transpose(normy)

def mmd_loss(source_features, target_features, kernel_mul=2.0, kernel_num=5, fix_sigma=None):
    batch_size = tf.shape(source_features)[0]
    total = tf.concat([source_features, target_features], axis=0)
    n_samples = batch_size * 2
    if fix_sigma:
        bandwidth = fix_sigma
    else:
        pairwise_dists = _pairwise_sq_dists(total, total)
        bandwidth = tf.reduce_sum(pairwise_dists) / (tf.cast(n_samples * (n_samples - 1), tf.float32))
    sigmas = [bandwidth * (kernel_mul ** i) for i in range(kernel_num)]
    XX = gaussian_kernel_matrix(source_features, source_features, sigmas)
    YY = gaussian_kernel_matrix(target_features, target_features, sigmas)
    XY = gaussian_kernel_matrix(source_features, target_features, sigmas)
    return tf.reduce_mean(XX) + tf.reduce_mean(YY) - 2 * tf.reduce_mean(XY)



# ----------------------------------------------------------
# Modified make_backbone to expose features and logits
# ----------------------------------------------------------
def make_backbone_with_feats(num_classes):
    base = MobileNetV2(
        input_shape=(120, 120, 3),
        include_top=False,
        weights="imagenet",
        pooling="avg"
    )
    feat = base.output  # features
    logits = layers.Dense(num_classes)(feat)  # raw logits
    # Model returns both logits and features (we will reference feat via intermediate model)
    model = Model(inputs=base.input, outputs=logits)
    feat_extractor = Model(inputs=base.input, outputs=feat, name="feat_extractor")
    return model, feat_extractor

# ----------------------------------------------------------
# CoDA model with adversarial + noise layers
# ----------------------------------------------------------
class CoDAModel(tf.keras.Model):
    def __init__(self, net1, net2, feat1, feat2, discriminator=None, noise_layer=None,
                 alpha=0.5, eta=0.3, num_classes=7, grl_lambda=1.0, **kwargs):
        super().__init__(**kwargs)
        self.net1 = net1
        self.net2 = net2
        self.feat1 = feat1
        self.feat2 = feat2
        self.discriminator = discriminator
        self.noise_layer = noise_layer
        self.alpha = alpha
        self.eta = eta
        self.num_classes = num_classes
        self.grl_lambda = grl_lambda

        self.loss_fn = tf.keras.losses.CategoricalCrossentropy(from_logits=True)
        self.bce = tf.keras.losses.BinaryCrossentropy()
        self.acc_metric = tf.keras.metrics.CategoricalAccuracy(name="accuracy")
        self.precision = tf.keras.metrics.Precision(name="precision")
        self.recall = tf.keras.metrics.Recall(name="recall")

        # for JS/discrepancy (we already used softmax + JS in original)
        self.eps = 1e-8

    def call(self, inputs, training=False):
        # unpack inputs
        (xs, ys), xt = inputs
        # just forward through one branch (net1) for warmup
        return self.net1(xs, training=training)

    def transferability_weights(self, p1, p2):
        # p1, p2 are softmax probs: [B, K]
        # cosine similarity per sample:
        dot = tf.reduce_sum(p1 * p2, axis=1)
        norm1 = tf.norm(p1, axis=1)
        norm2 = tf.norm(p2, axis=1)
        cos = dot / (norm1 * norm2 + 1e-8)
        lam = 1.0 - cos               # λ = 1 - cos
        lam = tf.expand_dims(lam, axis=1)  # [B,1]
        return lam
    
    def train_step(self, data):
        (source_x, source_y), target_x = data
        with tf.GradientTape() as tape:
            # source
            logits1_s = self.net1(source_x, training=True)
            logits2_s = self.net2(source_x, training=True)
            probs1_s = tf.nn.softmax(logits1_s)
            probs2_s = tf.nn.softmax(logits2_s)
            feats1_s = self.feat1(source_x, training=True)
            feats2_s = self.feat2(source_x, training=True)

            # target
            logits1_t = self.net1(target_x, training=True)
            logits2_t = self.net2(target_x, training=True)
            probs1_t = tf.nn.softmax(logits1_t)
            probs2_t = tf.nn.softmax(logits2_t)
            feats1_t = self.feat1(target_x, training=True)
            feats2_t = self.feat2(target_x, training=True)

            # classification loss
            loss1 = self.loss_fn(source_y, logits1_s)
            loss2 = self.loss_fn(source_y, logits2_s)
            clf_loss = loss1 + loss2

                        # discrepancy JS (classifier diversity) - same as before
            p1 = probs1_s; p2 = probs2_s
            m = 0.5 * (p1 + p2)
            js = tf.reduce_mean(
                tf.reduce_sum(p1 * tf.math.log((p1 + self.eps) / (m + self.eps)), axis=1) +
                tf.reduce_sum(p2 * tf.math.log((p2 + self.eps) / (m + self.eps)), axis=1)
            )
            disc_loss = js

            # Transferability-aware weights (on target)
            p1t = tf.nn.softmax(logits1_t); p2t = tf.nn.softmax(logits2_t)
            lam_t = self.transferability_weights(p1t, p2t)  # [B,1]

            # Domain adversarial loss (use GRL effect): predict domain from features
            # Build averaged features or concat features of both peers
            avg_feats_t = 0.5 * (feats1_t + feats2_t)
            avg_feats_s = 0.5 * (feats1_s + feats2_s)

            # apply gradient reversal by multiplying gradient through a custom op:
            grl = GradientReversal(hp_lambda=self.grl_lambda)
            rev_s = grl(avg_feats_s)
            rev_t = grl(avg_feats_t)

            d_s = self.discriminator(rev_s, training=True)  # source should be 1
            d_t = self.discriminator(rev_t, training=True)  # target should be 0

            # domain labels
            ds = tf.ones_like(d_s)
            dt = tf.zeros_like(d_t)

            # incorporate transferability weights for both source and target per paper
            # we expand weights for source as ones (or compute similarly if desired)
            adv_loss_s = self.bce(ds, d_s)  # could weight by λ_s if available
            # weight target adv loss per-sample by lam_t
            adv_loss_t = tf.reduce_mean(lam_t[:, 0] * tf.keras.losses.binary_crossentropy(dt, d_t))
            adv_loss = adv_loss_s + adv_loss_t

            # Optional: MMD between averaged features
            mmd = mmd_loss(avg_feats_s, avg_feats_t)

            # Noise co-adaptation: compute predicted noisy labels from features and classifier probs
            if self.noise_layer is not None:
                # use source feats and averaged probs (or per-network probs)
                avg_probs_s = 0.5 * (probs1_s + probs2_s)
                pz, _ = self.noise_layer(avg_feats_s, avg_probs_s)  # p(z|x,f) [B,K]
                # Treat source_y as possibly noisy noisy-label z; match pz to source_y
                noise_loss = self.loss_fn(source_y, tf.math.log(pz + 1e-8))  # crossentropy-like
            else:
                noise_loss = 0.0

            # total loss for feature extractor/classifiers: minimize clf + noise - alpha * adv - eta * disc + mmd*beta
            total_loss = clf_loss + noise_loss - self.alpha * adv_loss + self.eta * disc_loss + 0.1 * mmd

        # grads for all trainable variables (nets + noise layer + feat extractors + classifiers)
        train_vars = (self.net1.trainable_variables + self.net2.trainable_variables +
                      self.discriminator.trainable_variables + (self.noise_layer.trainable_variables if self.noise_layer else []))
        grads = tape.gradient(total_loss, train_vars)
        self.optimizer.apply_gradients(zip(grads, train_vars))

        # metrics update
        self.acc_metric.update_state(source_y, 0.5*(probs1_s + probs2_s))
        return {"loss": total_loss, "accuracy": self.acc_metric.result(),
                "adv_loss": adv_loss, "disc_loss": disc_loss, "noise_loss": noise_loss}
    
    def test_step(self, data):
        x, y = data
        logits1 = self.net1(x, training=False)
        logits2 = self.net2(x, training=False)
        avg_logits = (logits1 + logits2) / 2.0
        avg_probs = tf.nn.softmax(avg_logits)

        loss = self.loss_fn(y, avg_logits)

        self.acc_metric.update_state(y, avg_probs)
        self.precision.update_state(y, avg_probs)
        self.recall.update_state(y, avg_probs)

        precision_val = self.precision.result()
        recall_val = self.recall.result()
        f1_val = 2 * ((precision_val * recall_val) / (precision_val + recall_val + 1e-8))

        return {
            "val_loss": loss,
            "val_accuracy": self.acc_metric.result(),
            "val_precision": precision_val,
            "val_recall": recall_val,
            "val_f1": f1_val
        }

# ----------------------------------------------------------
# Evaluate
# ----------------------------------------------------------
import numpy as np
from sklearn.metrics import classification_report

def evaluate_model(model, test_ds, class_names):
    y_true, y_pred = [], []

    for batch_x, batch_y in test_ds:
        logits1 = model.net1(batch_x, training=False)
        logits2 = model.net2(batch_x, training=False)
        avg_logits = (logits1 + logits2) / 2.0
        preds = tf.argmax(avg_logits, axis=1).numpy()
        labels = tf.argmax(batch_y, axis=1).numpy()

        y_pred.extend(preds)
        y_true.extend(labels)

    print(classification_report(y_true, y_pred, target_names=class_names))

# ----------------------------------------------------------
# Dataset loader (with normalization + augmentation)
# ----------------------------------------------------------
def make_datasets(source_dir, target_dir, test_dir, batch_size=4, img_size=(120,120), seed=42):
    rescale = tf.keras.layers.Rescaling(1./255)

    # --- source (labeled) ---
    source_loader = tf.keras.utils.image_dataset_from_directory(
        source_dir,
        labels="inferred",
        label_mode="categorical",
        batch_size=batch_size,
        image_size=img_size,
        shuffle=True,
        seed=seed
    )
    source_ds = source_loader.map(
        lambda x, y: (rescale(tf.image.random_flip_left_right(x)), y),
        num_parallel_calls=tf.data.AUTOTUNE
    ).prefetch(tf.data.AUTOTUNE)

    # --- target (unlabeled) ---
    target_paths = glob.glob(target_dir + "/*.jpg")
    target_ds = tf.data.Dataset.from_tensor_slices(target_paths)

    def preprocess_target(path):
        img = tf.io.read_file(path)
        img = tf.image.decode_jpeg(img, channels=3)
        img = tf.image.resize(img, img_size)
        img = tf.image.random_flip_left_right(img)
        img = tf.cast(img, tf.float32) / 255.0
        return img

    target_ds = target_ds.map(preprocess_target, num_parallel_calls=tf.data.AUTOTUNE)
    target_ds = target_ds.batch(batch_size).shuffle(1000).prefetch(tf.data.AUTOTUNE)

    # --- dual domain dataset ---
    dual_ds = tf.data.Dataset.zip((source_ds, target_ds))

    def merge_batches(source_batch, target_images):
        source_imgs, source_labels = source_batch
        return (source_imgs, source_labels), target_images

    dual_ds = dual_ds.map(merge_batches, num_parallel_calls=tf.data.AUTOTUNE).prefetch(tf.data.AUTOTUNE)

    # --- validation dataset ---
    test_loader = tf.keras.utils.image_dataset_from_directory(
        test_dir,
        labels="inferred",
        label_mode="categorical",
        batch_size=1,
        image_size=img_size,
        shuffle=False
    )
    class_names = test_loader.class_names   # ✅ capture class names before mapping

    test_ds = test_loader.map(
        lambda x, y: (rescale(x), y),
        num_parallel_calls=tf.data.AUTOTUNE
    ).prefetch(tf.data.AUTOTUNE)

    return dual_ds, test_ds, class_names



# ----------------------------------------------------------
# Training function
# ----------------------------------------------------------
from datetime import datetime
def train_mobilenet():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join("Model_TF2", timestamp)
    os.makedirs(out_dir, exist_ok=True)

    num_classes = int(os.environ.get("CLASS_NUMBER", 7))
    batch_size = int(os.environ.get("BATCH_SIZE", 4))
    num_epochs = int(os.environ.get("EPOCH", 10))
    init_lr = float(os.environ.get("INIT_LR", 1e-4))
    alpha = float(os.environ.get("alpha", 0.5))
    eta = float(os.environ.get("eta", 0.3))

    
    target_dir = os.environ.get("T_DSET_PATH")
    test_dir = os.environ.get("TEST_DSET_PATH")
        # compute class weights from source dataset
    

    source_dir = os.environ.get("S_DSET_PATH")
    class_names = sorted(os.listdir(source_dir))
    y_labels = []
    for idx, cls in enumerate(class_names):
        y_labels.extend([idx] * len(os.listdir(os.path.join(source_dir, cls))))
    class_weights = compute_class_weight("balanced", classes=np.arange(len(class_names)), y=y_labels)
    class_weights = dict(enumerate(class_weights))
    # --- datasets ---
    dual_ds, test_ds, class_names = make_datasets(source_dir, target_dir, test_dir, batch_size=batch_size)

    # --- models ---
    net1, feat_extractor1 = make_backbone_with_feats(num_classes)
    net2, feat_extractor2 = make_backbone_with_feats(num_classes)
    # create discriminator(s) - paper shares domain discriminator D; we use one shared
    disc = make_domain_discriminator(input_shape=(feat_extractor1.output_shape[-1],))
    noise_layer = NoiseCoAdapt(num_classes=num_classes, hidden_dim=128)

    # compile models inside CoDA wrapper: pass discriminator & noise_layer into CoDAModel
    model = CoDAModel(net1, net2, feat_extractor1, feat_extractor2,
                    discriminator=disc, noise_layer=noise_layer,
                    alpha=alpha, eta=eta, num_classes=num_classes)
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=init_lr))

    # --- Warmup once to trigger CUDA/cuDNN compilation ---
    dummy_x = np.random.rand(1,120,120,3).astype("float32")
    dummy_y = np.zeros((1, num_classes), dtype="float32")  # still needed for input shape
    _ = model(((dummy_x, dummy_y), dummy_x), training=False)
    # -----------------------------------------------------



    # --- build model explicitly before training ---
    model.build(input_shape=[((None, 120, 120, 3), (None, num_classes)), (None, 120, 120, 3)])

    # --- callbacks ---
    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            filepath=os.path.join(out_dir, "best_coda_model.weights.h5"),
            save_best_only=True,
            monitor="val_f1",
            mode="max",
            save_weights_only=True,
            verbose=1
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_f1",
            patience=7,
            restore_best_weights=True,
            mode="max",   # ✅ explicitly say we want the highest val_accuracy
            verbose=1
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_f1",
            factor=0.5,     # reduce LR by 50% if stuck
            patience=3,
            mode="max", 
            verbose=1
        )
    ]

    # --- train ---
    history = model.fit(
        dual_ds,
        epochs=num_epochs,
        validation_data=test_ds,
        callbacks=callbacks
    )

    # --- save final weights ---
    model.save_weights(os.path.join(out_dir, "final_coda_model.weights.h5"))

    return history, class_names
