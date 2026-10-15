import tensorflow as tf

tf.random.set_seed(42)

import numpy as np
import os
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras import regularizers

class F1Score(tf.keras.metrics.Metric):
    def __init__(self, name="f1_score", **kwargs):
        super().__init__(name=name, **kwargs)
        self.tp = self.add_weight(name="tp", initializer="zeros")
        self.fp = self.add_weight(name="fp", initializer="zeros")
        self.fn = self.add_weight(name="fn", initializer="zeros")

    def update_state(self, y_true, y_pred, sample_weight=None):
        y_true = tf.argmax(y_true, axis=1)
        y_pred = tf.argmax(y_pred, axis=1)

        tp = tf.reduce_sum(tf.cast(y_true == y_pred, tf.float32))
        fp = tf.reduce_sum(tf.cast(y_pred != y_true, tf.float32))
        fn = fp  # simplified for multi-class

        self.tp.assign_add(tp)
        self.fp.assign_add(fp)
        self.fn.assign_add(fn)

    def result(self):
        precision = self.tp / (self.tp + self.fp + 1e-7)
        recall = self.tp / (self.tp + self.fn + 1e-7)
        return 2 * ((precision * recall) / (precision + recall + 1e-7))

    def reset_states(self):
        self.tp.assign(0.0)
        self.fp.assign(0.0)
        self.fn.assign(0.0)




source_base = '/mnt/c/KULIAH_S007/DomainAdaptation_Thesis/ISIC_Split_Data/ISIC_Split_Data-001'

IMAGE_SIZE = 224
SOURCE_BATCH_SIZE = 8
TARGET_BATCH_SIZE = 8
EPOCHS = 50
AUTO = tf.data.AUTOTUNE
LEARNING_RATE = 0.001
THRESHOLD = 0.95
LAMBDA_U = 0.3

def preprocess(image, label):
    image = tf.image.resize(image, (IMAGE_SIZE, IMAGE_SIZE))
    image = tf.cast(image, tf.float32) / 255.0
    return image, label

def load_dataset(base_dir, batch_size, shuffle=True):
    ds = tf.keras.utils.image_dataset_from_directory(
        directory=base_dir,
        labels='inferred',
        label_mode='categorical',
        batch_size=batch_size,
        image_size=(IMAGE_SIZE, IMAGE_SIZE),
        shuffle=shuffle,
        seed=42
    )
    return ds.map(preprocess, num_parallel_calls=AUTO).prefetch(AUTO)

#sementara val pakai test dulu
source_train = load_dataset(os.path.join(source_base, "train"), SOURCE_BATCH_SIZE)
source_val = load_dataset(os.path.join(source_base, "test"), SOURCE_BATCH_SIZE, shuffle=False)

#untuk sementara pakai dataset val nya
target_train = load_dataset(os.path.join(source_base, "val"), TARGET_BATCH_SIZE, shuffle=False)
target_test = load_dataset(os.path.join(source_base, "test"), SOURCE_BATCH_SIZE, shuffle=False)

class_names = sorted([d for d in os.listdir(os.path.join(source_base, "train")) if os.path.isdir(os.path.join(source_base, "train", d))])
num_classes = len(class_names)


class SampleDA(keras.Model):
    def __init__(self, model, lambda_u=1.0, tau=0.95):
        super().__init__()
        self.model = model
        self.lambda_u = lambda_u
        self.tau = tau
        self.loss_tracker = keras.metrics.Mean(name="loss")
        self.acc_tracker = keras.metrics.CategoricalAccuracy(name="accuracy")

        self.ce = keras.losses.CategoricalCrossentropy(from_logits=True)

    @property
    def metrics(self):
        return [self.loss_tracker, self.acc_tracker]

    def train_step(self, data):
        (source_x, source_y), (target_x, _) = data

        with tf.GradientTape() as tape:
            logits_src = self.model(source_x, training=True)
            loss_src = self.ce(source_y, logits_src)

            logits_tgt = self.model(target_x, training=True)
            probs = tf.nn.softmax(logits_tgt)
            confidence = tf.reduce_max(probs, axis=1)
            mask = confidence > self.tau
            pseudo_labels = tf.stop_gradient(tf.one_hot(tf.argmax(probs, axis=1), depth=logits_tgt.shape[-1]))

            loss_tgt = self.ce(pseudo_labels, logits_tgt, sample_weight=tf.cast(mask, tf.float32))
            total_loss = loss_src + self.lambda_u * loss_tgt

        grads = tape.gradient(total_loss, self.model.trainable_variables)
        self.optimizer.apply_gradients(zip(grads, self.model.trainable_variables))

        self.loss_tracker.update_state(total_loss)
        self.acc_tracker.update_state(source_y, logits_src)

        return {"loss": self.loss_tracker.result(), "accuracy": self.acc_tracker.result()}

    def test_step(self, data):
        x, y = data
        logits = self.model(x, training=False)
        loss = self.ce(y, logits)

        self.loss_tracker.update_state(loss)
        self.acc_tracker.update_state(y, logits)

        return {"loss": self.loss_tracker.result(), "accuracy": self.acc_tracker.result()}
    
def build_model():
    base = keras.applications.MobileNetV2(input_shape=(IMAGE_SIZE, IMAGE_SIZE, 3), include_top=False, pooling='avg')
    base.trainable = True
    inputs = keras.Input(shape=(IMAGE_SIZE, IMAGE_SIZE, 3))
    x = base(inputs, training=True)
    outputs = layers.Dense(num_classes)(x)
    return keras.Model(inputs, outputs)

steps_per_epoch = tf.data.experimental.cardinality(source_train).numpy()
total_steps = EPOCHS * steps_per_epoch

model = build_model()
sampleDA = SampleDA(model=model, lambda_u=LAMBDA_U, tau=THRESHOLD)
sampleDA.compile(optimizer=keras.optimizers.Adam(LEARNING_RATE))

total_ds = tf.data.Dataset.zip((source_train, target_train))
sampleDA.fit(total_ds, validation_data=source_val, epochs=EPOCHS)


sampleDA.model.compile(
    loss=keras.losses.CategoricalCrossentropy(from_logits=True),
    metrics=[
        keras.metrics.CategoricalAccuracy(name="accuracy"),
        keras.metrics.Precision(name="precision"),
        keras.metrics.Recall(name="recall"),
        F1Score(name="f1_score")
    ]
)


scores = sampleDA.model.evaluate(target_test, verbose=2)
print(f"Loss: {scores[0]:.4f}")
print(f"Accuracy: {scores[1]*100:.2f}%")
print(f"Precision: {scores[2]*100:.2f}%")
print(f"Recall: {scores[3]*100:.2f}%")
print(f"F1 Score: {scores[4]*100:.2f}%")

from sklearn.metrics import classification_report
import numpy as np

# Get predictions
y_true = []
y_pred = []
for x, y in target_test:
    preds = sampleDA.model.predict(x)
    y_true.extend(np.argmax(y.numpy(), axis=1))
    y_pred.extend(np.argmax(preds, axis=1))

print(classification_report(y_true, y_pred, target_names=class_names))
