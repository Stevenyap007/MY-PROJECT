# MCC (Minimum Class Confusion) 

This concept was created to overcome rigid forms of domain adaptation models, in this case referring to changes in model usage scenarios. For example, if a model is processed for a supervised domain adaptation format, then the model will perform poorly if it enters to handle unsupervised scenarios.

This concept will work as an additional calculation feature focusing on the target output. Its main focus is handling class confusion, which differs from some adversarial methods that only focus on domain alignment. This technique focuses on predictions in the target domain, which often makes the model unable to determine which is the correct class and which is the ambiguous class, therefore this technique is tasked with minimizing that confusion level.

The main components consist of:

* **Probability Rescaling**, this stage functions to rescale the output results so that a more varied class probability value is obtained and it is not overconfident.

* **Uncertainty Reweighting**, is a feature filtering stage. Feature results that have low confidence will be ignored while high confidence will be reweighted to be used as a learning reference. For example, images with probabilities showing doubt between two classes (e.g., resembling Melanoma and Nevus at the same time) are given higher weights, because these images are the most useful for mapping network confusion.

* **Class Correlation**, class prediction probability results will be inputted into a confusion matrix format (3.23);

* **Minimization**, the next process is to eliminate overlapping outputs on the matrix so that it is filtered and the model will have more separated prediction results and the level of confusion between classes can be suppressed (3.24).

The working steps are:
* Incoming data extracts source and target features.
* Source and label will be treated with classification cross entropy.
* The target extraction results will have their raw logits taken and enter the MCC process.
* Enter the MCC stages:
  * Probability rescaling = a stage to soften the class prediction results in one sample before entering the softmax using a temperature parameter, making the prediction results of each class closer and the location of inter-class confusion more visible.
  * Uncertainty Reweighting = when the results of the previous step show a high level of confidence in a particular class and compete fiercely, a high weight will be given. Whereas in results where every class has low probability scores, a low weight is given (calculating the distance between classes to determine whether the image is confident or not by calculating entropy, then the lowest entropy is given the highest weight).
  * Class Correlation (The Matrix) = creating a matrix by multiplying the class probabilities with their weights to form a correlation matrix.
  * Category Normalization = normalizing the matrix.
  * MCC-loss = obtained from the sum of Off-Diagonal values of the correlation matrix.

This MCC also acts like an additional layer, especially in the process of managing predictions on target data. On this occasion, 2 models will be taken as comparison materials for the performance of adding the MCC system. The first is DAN (Deep Adaptation Network) and DANN (Domain Adversarial Neural Networks). Both models have been discussed previously and both have the best performance in their fields compared to other previous models.

## Dan_mcc_mobilenetv2.py (code explanation)

For the MCC mechanism file with the DAN model, maybe some functions will be familiar with some previous code, especially in the DAN model architecture. Some things to note are:

1. This MCC Loss is a code block that fully represents the MCC method. Unlike MMD which receives source and target features, the forward function in pure MCC ONLY receives logits from the target data.

   The MCC flow is:
   a. Target predictions are smoothed with softmax.
   b. Entropy and inter-class weights are calculated.
   c. Correlation matrix creation.
   d. Then its minimization: Summing the entire contents of the matrix then subtracting its main diagonal values (the correct class).

2. Then for the DAN + MCC Integration:
   In the DAN section, the MMD loss will be calculated while the MCC will have its MCC loss calculated. Then all of that will be inputted into the total loss calculation which consists of classification cross entropy loss for the source data, with its MMD and MCC loss, where the total loss will be used to update the model weights.

3. Then for its notebook it consists of:
   a. Dataset Initiation and Training Execution
   b. Model Checkpoint Loading
   c. Metric Evaluation
   d. Visualization

Moving on to the DANN section.

## Dann_mcc_mobilenetv2.py (code explanation)

For the MCC mechanism file with the DANN model, maybe some functions will be familiar with some previous code, especially in the DANN model architecture, there is a gradient reversal layer that runs the backpropagation task, and for the others, some things to note are:

1. The total loss calculation now uses DANN parameters, namely classification loss, domain loss, and MCC loss.

2. Then for its notebook it consists of...

What needs to be underlined is that the MCC technique applied to the DANN adversarial method is slightly simplified seeing that the adversarial technique is already computationally consuming. This is also considered because when applying the full MCC theory, the performance is almost the same, just slightly below the performance tested here.