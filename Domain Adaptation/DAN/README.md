# DAN (Deep Adaptation Network) 

This method uses Multiple Kernel Maximum Mean Discrepancy (MK-MMD), where MMD calculates the distance between source and target features in a Reproducing Kernel Hilbert Space (RKHS) mapping so that both features can be juxtaposed together based on the reference of mean embeddings as the center (3.1). However, this technique relies heavily on the kernel used, therefore MK is needed, which can provide a set of kernels so that MMD does not rely solely on a single-kernel.

*   Incoming data -> feature extraction -> enter the top layer -> in the connected layer, source and target features enter the RKHS format and create a mean embedding (MMD) where the center is determined by MK -> Input loss will continue to the next minmax loop process until the final layer -> the stages are repeated and ended with prediction.
*   Source and target feature extraction and representations are mapped to the RKHS format.
*   Multiple kernel = gives a score to determine the level of similarity between source and target samples.
*   MMD = calculates the mean embedding / midpoint between source features and target features.

## Dan_mobilenetv2.py (code explanation)
This file is the core of the model consisting of many functions that will be executed later.

1. Starting with hyperparameter configuration.
2. Basic sample transformation.
3. Entering the model creation, starting with a pretrained model as the backbone, namely mobilenet v2 & def forward which provides logits feedback and features, then the classifier which becomes the classification layer.
4. Then GaussianKernel to calculate the squared distance between data points, and then the MK MMD function with the principles explained previously.
5. Entering the training cycle consisting of:
    a. Load data
    b. Cross entropy loss calculation
    c. Then mmd_loss calculation every 5 iterations
    d. And ending with total loss to be used as feedback for creating new weights in the training iteration
    e. Ended with evaluation and saving the model

## IPYNB (code explanation)
Next, the notebook file is more or less an execution file done by calling methods or functions that have been created in the previous Python file.

