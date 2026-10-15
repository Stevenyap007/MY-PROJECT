# DANN (Domain Adversarial Neural Networks) 

Unlike DAN or JAN which rely on statistical calculations, this method uses a deep learning machine learning system where this technique has 3 main components, namely:

1. Feature Extractor, as the name implies, for feature extraction.
2. Label predictor, to classify the class of an image.
3. Domain classifier, tasked with distinguishing which parts belong to the source domain and which are from the target domain.

The stages of this model proceed by:
* Feature extraction will generate features for the source and target.
* Then the next step will run in parallel on the label predictor and domain classifier.
* Label predictor = guesses the label for the source domain, OUTPUT, label prediction loss.
* Domain Classifier = guesses the domain origin of the sample whether it is source/target, OUTPUT, domain classification Loss which will undergo a reverse from the gradient reversal layer so that later the feedback returned to the feature extractor is feedback to do the opposite of the domain classifier results.
* Backpropagation = after calculating the total loss, it will proceed to this stage to minimize classification loss and maximize domain classifier loss by providing input to the feature generator to create features that are domain invariant but also discriminative.

## dann_mobilenetv2.py (code explanation)

This file consists of:
1. The data load function.
2. Then also the initialization of the mobilenet v2 backbone used.
3. Classifier and discriminator, the 2 main components explained previously.
4. Gradient reversal layer with a backpropagation mechanism where when starting from the feature extractor to the 2 main classification components, it will be forwarded as usual, but when the output of the domain discriminator returns to the feature extractor, the GRL will return a negative result or the opposite result.
5. Evaluation function.
6. And the training function where the total loss consists of cross entropy loss in the source domain with the domain loss obtained.

## DANN - ep 2 (code explanation)

Next, the notebook file is more or less an execution file done by calling methods or functions that have been created in the previous Python file.

ALSO THERE IS A VGG16 VERSION USED AS A COMPARISON FOR MODEL PERFORMANCE WITH THE APPLICATION OF DIFFERENT BACKBONES AND THEIR IMPACTS.