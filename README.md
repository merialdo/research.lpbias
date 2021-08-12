# research.lpbias

We study the effect of bias in Link Prediction (LP) models on Knowledge Graphs (KGs). 
We define three main types of bias in the Link Prediction context: 

- **Type 1 Bias**: A tail prediction <*h*, *r*, *t*> is prone to Type 1 Bias if the training facts mentioning *r* tend to always feature *t* as tail. 
For example, the tail prediction <*Barack_Obama*, *gender*, *male*> is prone to bias if the vast majority of gendered entities in the training set are males:
This artificially favours the prediction of *Barack_Obama*'s gender as *male* too.

- **Type 2 Bias**: A tail prediction <*h*, *r*, *t*> is prone to Type 2 Bias if:
  - *r* is a one-to-many or a many-to-many relation;
  - in training, whenever an entity *e* is seen as head for relation *r*, the training fact <*e*, *r*, *t*> also exists.

  This type of bias describes relations that tend to have a "default" tail that is almost always a correct answer. For instance, the tail prediction <*Cristiano_Ronaldo*, *language*, *English*> is prone to bias if most people in the training set also speak *English* (in addition to other languages).

- **Type 3 Bias**: A tail prediction <*h*, *r*, *t*> is prone to Type 3 Bias if 
  - a relation *s* is often seen co-occurring with *r*
  - the fact <*h*, *s*, *t*> is present in the training set.

  For example, in the `FB15k` dataset the producer of a TV program is almost always its creator too; this may lead to the biased assumption that who creates a program can also be predicted as its producer.

We analyze the presence of bias on the 5 best-established datasets in LP literature: `FB15k`, `WN18`, `FB15k-237`, `WN18RR`, and `YAGO3-10`. 
We include them in the `data` folder of this repository.

## Assessing bias in LP Datasets

We describe in this section the commands that allow to identify, for each test prediction across all datasets, if it is prone to bias.
Each of the commands in this section will save their findings in files in the `bias_data` folder.
Note that in this repository **we already include all these computed files**, therefore it is not required to run these commands to verify our end-to-end results; we report them nonetheless for the sake of reproducibility.

- To verify, for each test prediction across all datasets, if it is prone to Type 1 Bias, run the command:
  ```python
  python3 scripts/extract_biased_test_facts_type_1.py
  ```

- To verify, for each test prediction across all datasets, if it is prone to Type 2 Bias, run the command:
  ```python
  python3 scripts/extract_biased_test_facts_type_2.py
  ```

- To verify, for each test prediction across all datasets, if it is prone to Type 3 Bias, run the command:
  ```python
  python3 scripts/extract_biased_test_facts_type_3.py
  ```

In our work we also verify in datasets WN18 and WN18RR the effects of inverse and symmetric relations.
The following commands check, for any test prediction in these datasets, if the relation has one of such properties; they act analogously to the described above commands used to verify the presence of biases.

- To verify, for each test prediction in WN18 or WN18RR, if its relation is inverse of another relation in the dataset, run the command:
  ```python
  python3 scripts/extract_inverse_test_facts.py
  ```

- To verify, for each test prediction in WN18 or WN18RR, if its relation is symmetric, run the command:
  ```python
  python3 scripts/extract_symmetric_test_facts.py
  ```

## Bias effects on LP datasets
We assess the number of bias-prone test predictions in LP datasets with the following command:
```python
python3 scripts/compute_dataset_size_removing_bias.py --dataset FB15k --bias 1
```

Acceptable values for the `--dataset` parameter are `FB15k`, `WN18`, `FB15k-237`, `WN18RR`, and `YAGO3-10`. ; acceptable values for the `--bias` parameter are `1`, `2`, `3` and `any`.
Using value `any` for the `--bias` parameter, all test facts prone to any of the 3 bias types will be taken into account.

The results show that significant portions of `FB15k`, `FB15k-237` and `YAGO3-10` are affected by bias:
<p align="center">
<img width="70%" alt="hyperparams" src="https://user-images.githubusercontent.com/6909990/129218450-fd2e1dc8-c00b-4e32-b70e-4e666998de8b.png">
</p>

## Effects of bias on performance of LP models

We verify the effect of bias on the behaviour of multiple LP models. 
We first compute their predictive performance across all test predictions; we then filter away the bias-prone predictions and recompute the evaluation metrics.
If in the latter scenario results are worse than the former, this means that the presence of bias actually affected the behaviour of LP models.
In other words, when this happens bias has made the bias-prone predictions easier than average: this is why removing them decreases the overall performance of models.

We use as a starting point the publicly available evaluation results of *19* LP models computed in (our recent Comparative Analysis of LP models)[https://github.com/merialdo/research.lpca].
For the sake of completeness, we include in this repository, in folder `comparative_analysis_results`, a copy of the specific files that we have used as an input in our work.

The analysis on the effects of the various types of bias on all models can be run using the following command:

```python
python3 scripts/compute_performance_removing_bias.py --dataset FB15k --bias 1
```
As in the previous command, acceptable values for the `--dataset` parameter are `FB15k`, `WN18`, `FB15k-237`, `WN18RR`, and `YAGO3-10`; acceptable values for the `--bias` parameter are `1`, `2`, `3` and `any`; using value `any` for the `--bias` parameter, all test facts prone to any of the 3 bias types will be taken into account.

The overall results show that the 3 forms of bias taken into account heavily affect LP models on `FB15k`, `FB15k-237` and `YAGO3-10`: 

<p align="center">
<img width="80%" alt="hyperparams" src="https://user-images.githubusercontent.com/6909990/129210983-99685158-18b0-49bc-8218-b321dd3a1199.png">
</p>

Datasets WN18 and WN18RR are apparently more robust to bias. However this does not make them more desirable, as the main reason of this robustness seems to be the pervasive presence of inverse and symmetric relations.

<p align="center">
<img width="80%" alt="hyperparams" src="https://user-images.githubusercontent.com/6909990/129211000-c59811a2-421d-4759-b56c-58b387d3923b.png">
</p>
