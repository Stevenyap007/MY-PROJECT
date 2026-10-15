Before starting, it needs to be underlined that this has entered another section, namely domain adaptation with a Transferability / Robustness-Aware approach, where some of these methods are methods that have the model concepts that have been discussed previously, but their layers are added or one of the mechanisms in the previous model architecture is given innovation or development.

Ok Transferable Attention for Domain Adaptation

# TADA (Transferable Attention for Domain Adaptation) 

As the name "Attention" suggests, this model has the main idea of selecting parts that are assumed to need more attention compared to other parts. Then the remaining parts can be categorized as "negative transfer", because they can include less useful features such as the background or completely different features and only provide a bad learning burden.

This model works by adding 2 attention features into the standard adversarial domain adaptation mechanism, namely: Transferable Local Attention, where this feature will divide the feature map into several parts to be given to a discriminator that assesses the parts that make a large contribution to the system, then it will recalculate the overall score of the feature map (3.16). This will make the model focus more on the classification object rather than the background; Transferable Global Attention, unlike the previous feature that focuses on image details, this feature functions to assess the entire image whether the image can be used as learning material, where the image looks indistinguishable, or is just an outlier image and damages the learning process.

The working steps are:

* Incoming data, its features are extracted, and in the feature extraction stage, it is also divided into regions that form a local feature map, so 1 image consists of several regions.
* Local attention Module = Then in each region, a local discriminator will be provided, which calculates the entropy to determine the amount of weight in each region.
* After that, each local feature is combined and inputted to the global attention to determine whether the entire image is feasible to be transferred or not by assigning weight.
* Enter the total loss calculation among = classification loss (loss from label prediction), attentive entropy loss (focuses to force the model to select target samples that can be transferred based only on input from global attention), adversarial transfer loss (loss from local and global to make the feature generator provide features that are indistinguishable).
* The continuation is a minmax process like several previous models to minimize class loss and maximize domain adversarial loss.

This TADA acts like an additional layer, especially in the feature extraction process which is developed with the application of an attention system. On this occasion, 2 models will be taken as comparison materials for the performance of adding the attention system, the first is ADDA or Adversarial Discriminative Domain Adaptation, and DANN or Domain Adversarial Neural Networks.

## attention_adda_mobilenetv2.py (code explanation)

For the attention mechanism file with the ADDA model, maybe some functions will be familiar with some previous code, especially in the architecture in the ADDA model. Some things to note are:

1. In the encoder function, the resulting feature outputs include 2 formats, namely, an intact feature map with spatial size ([B, C, H, W]) for pixel-by-pixel analysis, and a pooled vector ([B, C]) for global image analysis.
2. Then the creation of 2 discriminator functions that act as local attention and global attention.
3. And lastly, for the notebook file, it is more or less the same.

Moving on to the DANN section

## attention_dann_mobilenetv2.py (code explanation)

For the attention mechanism file with the DANN model, maybe some functions will be familiar with some previous code, especially in the architecture in the DANN model. Some things to note are:

1. In the encoder section, there are 2 feature maps just like before to generate local and global features.
2. The addition of local and global discriminators that produce local and global losses that are taken into consideration in calculating the total loss.
3. And lastly, for the notebook file, it is more or less the same.