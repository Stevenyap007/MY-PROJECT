# CONCLUSIONS AND RECOMMENDATIONS

## 5.1. Conclusions

The research on developing a domain adaptation model with an unsupervised scenario against data limitations based on mobilenetv2 yields several conclusions, namely:

1) Based on the experimental results, the adoption of the Domain Adaptation framework to build a skin disease prediction model is carried out by overcoming the domain shift, namely the difference in format and distribution characteristics, between the learning source data and the target data. The application of this framework has proven to be an adaptive and appropriate step for transferring model knowledge between different domains.

2) The domain adaptation development process can be optimized through three approaches, namely: distribution alignment approaches, which focus on aligning the distribution of features between the two domains; Decision boundary approaches, which are carried out by modifications at the classifier level in the interpretation of a feature; Transferability / Robustness approaches, which focus on other detailed matters in the domain adaptation process.

3) Analysis of the potential of Domain Adaptation in conditions of limited data availability is carried out by an evaluation process of the model using a performance matrix. Based on these metrics, the performance level of each tested approach can be compared to see to what extent the model is able to maintain its predictive ability.

4) The final evaluation results of each domain adaptation model show that the use of domain adaptation provides an increase in performance compared to regular transfer learning models. The baseline model results have an accuracy of 18%, which is then outperformed by the three approaches used such as: Distribution Alignment, with an accuracy scale of 14-30%; Decision Boundary, with an accuracy scale of 26-27%; Transferability & Robustness, with an accuracy scale of 12-34%. Unfortunately, the model can be said to be not yet ready to face real-world scenarios.

## 5.2. Recommendations

Based on the conclusions obtained, the recommendations that can be applied to the development of this research are as follows:

1) Recalculating class distribution. Experimental results show that some models tend to ignore classes with a small number of samples; therefore, a distribution recalculation process on the classes is needed.

2) Selection of pretrained or backbone. This refers to a safe model deployment process in the medical world; however, by applying this process, the computational load and required devices are more expensive.

3) Applying multi-source DA. This is to cover variations in skin diseases, adding knowledge specifically on dark skin data so that the model is more general in predicting.

4) Applying multi-source multi-target DA. This is still related to the previous problem where the image samples in the target data also need to be added with variations and a balanced number of samples.

5) Performing model compression. This is a development of the previous recommendation where in its training it still uses a model with large parameters but is followed up with model compression, to adjust to simpler devices in the future.

6) Applying Knowledge Distillation. This is an alternative to the previous recommendation by applying a "teacher-student" mechanism, where 2 models will be trained with large and small parameters, where the large model will provide knowledge to the small model to obtain performance resembling the large model.

7) Applying few-shot domain adaptation. Here, the model is not trained completely unsupervised without using labels, but instead uses several labeled samples in its training process.