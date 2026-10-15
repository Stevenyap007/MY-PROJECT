# CDAN (Conditional Domain Adversarial Network) 

This model also departs from the assumption that the process performed by the DANN model does not necessarily consider the condition of class differences and only align features at the domain level.

This model is a combination of the theory in the JAN model which applies Joint Maximum Mean Discrepancy with the application of DANN's backpropagation training with a gradient reversal layer.

The stages consist of:
1. Load data
2. Then the data will enter 2 main components, namely:
   a. Feature extraction = will perform feature extraction
   b. Label classifier = will calculate class probability predictions
3. Then both components are entered into the Multilinear conditioning process to combine vectors in features and predictions.
4. Then the multilinear map's entropy will be calculated, or it can be called the entropy conditioning step.
5. After that, the results are inputted into the discriminator whose job is to predict the domain.
6. And ends with the backpropagation process when providing feedback from the discriminator so that the next feature extraction process is smarter at fooling the discriminator.

## CDAN_mobilenetv2.py (code explanation)

This file is the core of the model consisting of several parts that might be the same as the functions in the DANN method or a bit from JAN.
1. The first thing is related to GRL for backpropagation.
2. Moving on to the backbone and classifier, namely using mobilenetv2.
3. The domain discriminator for source domain or target domain classification.
4. This CDAN feature is for the Multilinear conditioning process that combines features and prediction percentages so they can be inputted to the discriminator.
5. Then each of these functions is combined for the training process; the total loss is calculated from the cross entropy loss of the source domain with the adversarial loss outputted from the discriminator.
6. And main for its looping.

## CDAN - ep 1 (code explanation)

1. Directory and Data Preparation
2. Model Training via CLI
3. Weight Loading
4. Evaluation and Classification Matrix
5. AI Performance Visualization