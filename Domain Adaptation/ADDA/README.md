# ADDA (Adversarial Discriminative Domain Adaptation) 

The ADDA technique emerged as an anticipation in handling the previous technique, namely DANN. This technique assumes that the feature extraction process in the DANN model is less effective because feature extraction is applied to both data sets at once (source and target), which could affect the bias level of the generated features.

The ADDA technique, as a solution, performs two feature extraction processes: first is the source encoder and then the target encoder. These stages consist of:

1. Load data
2. Pre-training, this stage is a simple feature extraction stage on the source data along with its predictions as the source encoder (3.6);
3. Adversarial Adaptation, after feature extraction, the source encoder layer will be frozen and used as a reference for the next stage, namely training the target encoder. It is then ready to be forwarded to the Discriminator to determine which domain the features come from. Simultaneously, the target encoder is trained to manipulate Fitzpatrick images into features that are so identical to ISIC features that the Domain Discriminator is fooled and considers them as the same single dataset.
4. Testing, this is the trial stage of feeding unlabeled target images into the model to evaluate the model's performance.

## ADDA_mobilenetv2.py (code explanation)

This file consists of:

1. Several initial requirements regarding its data handling.
2. We will focus on the pre-trained function, starting with the creation of the source encoder that uses Cross-Entropy Loss or Focal Loss as a supervised learning system normally runs.
3. Then the weights obtained are forwarded to this target adaptation function and become the initial feedback for how the discriminator works.
4. Then it ends with an evaluation.

## ADDA - ep 2 (code explanation)

Next, the notebook file is more or less an execution file done by calling methods or functions that have been created in the previous Python file.

ALSO THERE IS A VGG16 VERSION USED AS A COMPARISON FOR MODEL PERFORMANCE WITH THE APPLICATION OF DIFFERENT BACKBONES AND THEIR IMPACTS.