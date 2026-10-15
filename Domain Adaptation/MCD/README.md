Before starting, it needs to be underlined that this has entered another section, namely domain adaptation with a decision boundary approach where the level of model improvement is more aimed at the classifier layer, ok.

# MCD (Maximum Classifier Discrepancy) 

The hallmark of this method is the addition of a classifier layer, so there are 2 classifiers that confirm each other's predictions before producing the prediction output.

The stages of this method consist of:

1. Basic initialization: Generator and 2 classifiers with source data. These 3 main components are the ones that will be trained with source domain data, then
2. Tested with target data and minmax adjustments are made:
   a. Maximizing Discrepancy = the generator will be frozen and update the Classifiers to provide prediction outputs that are different from each other.
      i. The discrepancy value is calculated using L1-distance.
   b. Minimizing Discrepancy = conversely, the classifiers are frozen and update the generator to produce features that are acceptable to both classifiers.

## MCD_mobilenetv2.py (code explanation)

Ok, for the file, some of its main driving functions consist of:

1. Starting with a parser which can be skipped because it is a kind of default setting for hyperparameters and others.
2. Then the model architecture consists of:
   a. feature extractor or generator
   b. And its classifier
3. Then, for an overview of the use of the 2 classifiers, their application can be seen when entering its evaluation and training.
4. In the training stage, loss_A illustrates the loss with cross entropy calculation between G, F1, and F2 for the source domain data,
   then loss B illustrates the distance of the difference between the two classifiers when juxtaposed to the target data and its final result is used to perform the maximize discrepancy stage between classifiers,
   while loss C acts as an update process for the generator's adaptation level which acts to perform the minimize discrepancy stage.

## MCD - ep 2 (code explanation)