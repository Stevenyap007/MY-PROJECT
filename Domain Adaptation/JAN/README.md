# JAN (Joint Adaptation Network) 

The previous video discussed DAN, and now we will focus on the development of that method, namely JAN (Joint Adaptation Network). The points of change regarding its development are already visible from its name, with the keyword being JOINT. This joint principle is a concept that accounts for a model capable of considering the level of feature suitability between the source and target, but also includes the level of label suitability between the source and target.

This mechanism is calculated through a Tensor product system; therefore, the mapping used here is called the tensor product of Hilbert Space.

The stages include:
* Feature extraction
* The tensor product of Hilbert Space is taken, which is a collection of kernels from each layer (FC layer).
* Joint Maximum Mean Discrepancy = calculates the distance between the tensor product embedding of the source domain and the tensor product embedding of the target domain.

## Jan_mobilenetv2.py (code explanation)

This file is the core of the model consisting of several parts that might be the same as DAN, the differences are in:
1. JointMMD, which has a distance calculation between fs and ft for features, and ys and yt for predicting its label scores. This is also present in its Gaussian kernel which calculates k feat and k pred.
2. Then the same backbone, mobilenetv2, for lightweight parameter levels.
3. Data loader along with its basic transforms.
4. And entering the training process where the total loss consists of cross entropy loss, JMMD distance, and JMMD loss.
5. And the evaluation function at the end.

## JAN - ep 1 (code explanation)

Next, the notebook file is more or less an execution file done by calling methods or functions that have been created in the previous Python file.
