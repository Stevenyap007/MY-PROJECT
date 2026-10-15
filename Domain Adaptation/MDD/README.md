# MDD (Margin Disparity Discrepancy) 

Similar to MCD because there are 2 classifiers, what distinguishes them is that the two classifiers do not act as boundaries to align ambiguous features so that the created features move away from the ambiguous line of the two classifiers, BUT there are 2 classifiers: 1 is tasked with determining the class label, and 1 is tasked as a domain discriminator so that the ambiguous line or margin can be aligned to a safe margin (ambiguous boundary) (able to distinguish domains and classes).

So there are 3 parts: feature generator, main classifier, and auxiliary classifier.

* The main classifier will predict its source label.
* The aux classifier will identify samples that have ambiguous labels.
* The aux classifier will side with the source domain and reject samples from the target domain, the results of both losses will become the MDD input.
* MDD = calculates the difference between the main classifier and aux classifier results.
* + the resulting loss will become feedback to maximize its performance in determining its boundaries to decide whether the sample belongs to the source or target label.
* On the other hand, feedback is also given to the feature generator to minimize the distance range of feature differences between source and target so that because the distance is small, the aux classifier will be confused in determining its boundaries and let the target features pass into the source group.
* In the end, the aux classifier will be discarded, leaving the main classifier which can already accept both source and target features.

## MDD_mobilenetv2.py (code explanation)

Ok, for the file, some of its main driving functions consist of:

1. Unsupervised data load function.
2. The MDD model, consisting of the mobilenet feature generator, then classifier 1, then the auxiliary classifier (`self.classifier_adv`).
3. The MDD technique, which determines the boundaries of which auxiliary classifier sides with the main classifier and which does not.
4. Evaluation and
5. Its training.