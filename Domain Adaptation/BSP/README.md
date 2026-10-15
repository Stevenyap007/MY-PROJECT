# BSP (Batch Spectral Penalization) 

This concept is a concept developed to improve domain adaptation models that run adversarially such as ADDA or DANN. The reason lies in the adversarial concept which focuses on making the features of the source and target close but makes the features less discriminative towards classes, with the initial assumption that when the feature alignment process occurs, the model tends to take some dominant features so that other features do not develop.

The main feature used is the calculation of Batch Spectral Penalization (BSP) by applying Singular Value Decomposition (SVD) to extract dominant features between the source and target (3.14). Then, this BSP Loss will be combined into the standard calculation system of the adversarial model, so that ultimately the output produced is the result of the calculation between Classification error, Domain adversarial loss, and BSP penalty (3.15).

In essence, this BSP mechanism will track dominant features and dampen them so that the model will learn features broadly and not lean towards dominant features because the dominant features are dampened by this BSP technique.

The process involves:

* The model will receive an input batch of source and target images, OUTPUT = source and target feature matrix.
* Entering into 3 parallel processes:
  * Classification task, determining the class label.
  * Adversarial task, determining the domain of a sample.
  * BSP task, calculating the eigenvectors of both domains, calculated and processed by SVD to find out which dominant features will become the input for BSP loss to dampen the model's performance from training only on those dominant features.
* Calculate Total loss = the result of classification loss + adversarial loss + and BSP.
* The process proceeds like a normal adversarial; when backprop occurs, the BSP feedback will make the generator create features that are indistinguishable in their domain but also develop on the side of other features besides the dominant features.

## bsp_dann_mobilenetv2.py (code explanation)

In this trial, the adversarial method used is DANN. This is considered looking at the performance of ADDA which is not yet significant on the skin image data used. The components that will be in the code might be somewhat the same as the DANN method components, so I will focus on the distinguishing points, more towards the extended components such as:

1. The BSP loss function, performing Singular Value Decomposition operations to break down the feature matrix into three algebraic components. And ending with returning the compressed features.

2. Then for the training, the total loss consists of the classification loss on the source data, then the adversarial loss from the discriminator, and the BSP loss mentioned earlier.