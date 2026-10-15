# CoUDA (Collaborative Unsupervised Domain Adaptation)

The system runs by creating 2 neural network systems that are connected to give each other learning weights. If a sample is difficult to recognize by both networks, then the sample will be categorized and given a larger learning weight so that the training process will focus on that sample.

It needs to be underlined that although it looks familiar because the dual system in 1 model has been applied before, this model also has its own characteristics. For example, compared to ADDA, this model is pure 2 networks, whereas ADDA, although using 2 encoders, its classification layer remains 1, or when compared to the MCD method which is the opposite, 1 encoder 2 classifiers.

This model consists of 3 main parts, namely:

*   **Collaborative domain adaptation:** in this stage a sample's weight will be assessed based on the output results of both networks. If both networks feel the sample is difficult to identify, then a larger weight will be given to that sample (3.18);
*   **Collaborative Noise adaptation:** is a feature to combine knowledge from both networks. This layer is used to help both networks understand the noise in labels (3.19);
*   **Classifier Diversity Maximization:** this is an adversarial training process with additional loss using Jensen-Shannon (JS) divergence to ensure that the two networks remain different from each other (3.20).

The model's working mechanism process is =

1. Initialization of 2 networks, so there are 2 feature extraction and 2 classification layers.
2. Input source and target data; in the source section, potentially noisy labels are also taken.
3. Entering the 3 stage modules:
   a. Collaborative DA, takes the predicted output results from the 2 networks, calculates the cosine similarity; the greater the difference, the greater the weight given, so the model knows that the sample needs more attention.
   b. Collaborative noise adaptation = works by receiving feature inputs and predictions from the 2 networks; this is used to calculate label predictions and their accuracy levels against true labels or just noisy labels, resulting in focal classification loss.
   c. Classifier diversity maximization = used to ensure both networks remain different and do not fully copy each other, calculated with JS divergence.
4. All 3 modules are combined to calculate the total loss; the total loss result will be used to minimize errors from the domain discriminator and maximize the level of generated features to be indistinguishable (with the backprop system and GRL).
5. Test with target data.

## train_dual_Keras_Model2.py (code explanation)

Ok, getting into its core mechanism file, at first glance some functions might look familiar:

1. There is a performance metric function.
2. Then focal loss.
3. Gradient reversal layer that runs the backpropagation system.
4. Domain discriminator to determine the source data and which is the target.
5. Noise co-adaptation layer as explained previously.
6. MMD loss and mobilenet backbone.
7. Then in the training stage, you can see the creation of 2 networks denoted by net1 and net2, its features are also 2 with the same prediction probability values 2.
8. There is also a collaborative weight function that executes the Collaborative DA process to calculate the distance between the two networks and assigns weights so the model can have a priority scale.
9. There is also disc_loss as a limiting parameter so that the 2 networks still have their respective characteristics and do not assimilate into each other.
10. Then finally there is noise_loss, determining whether the label prediction result is noise or not.
11. Lastly, all of them become materials for calculating the total loss.

As for the execution notebook, it is more or less the same.

And there are also initial experiment results here, where this mechanism emphasizes the dual network concept more than the 3 main components of CoUDA.