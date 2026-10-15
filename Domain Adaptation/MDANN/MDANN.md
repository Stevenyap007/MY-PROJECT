# MDANN (Multiple Domain Adversarial Neural Network) 

This model offers a domain adaptation process as well as a bias reduction process formed from several demographic attributes in the image.

If you notice the name DANN is mentioned again in this project, it is because this model's concept is similar to DANN but there is a slight improvement or addition of layers, specifically in the discriminator layer which usually only has a domain discriminator. This method adds other layers; the number of layers depends on the needs of the model's designation. Like in this case, the addition of the discriminator layer used will be designated to determine demographic details that want to be ignored so that the model can learn things without being fixated on specific bias details.

This model consists of 3 main parts (3.25), namely:

* **Feature Extractor**, which works as its name implies, this layer functions to extract features from images and provide representations in a feature map format;
* **Predictor**, functioning as the main classification layer, where this is the class determiner;
* **Adversarial Module**, is an additional layer that works to detect sensitive details related to demographics, such as skin color, gender, age, and so on, where this layer is trained adversarially and also applies a backpropagation system with a Gradient Reversal Layer (GRL).

## IPYNB FILE

Go straight to the notebook because this MDANN's layer addition is considered custom, so there is a trial and error process, therefore the code is implemented in the notebook.

1. Starting from the data preparation, for fitz there is an addition of data regarding demographic details of skin color ranges which becomes a factor that the model will select later.

2. Then for the MDANN architecture itself, there is:
   a. Backbone pretrained feature extractor mobilenetv2
   b. There is a domain discriminator and an additional fairness discriminator
   c. Then in the training, there will be input for disease loss, domain loss, and fairness loss as the model's feedback update during its training.