import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.abspath(__file__), os.path.pardir, os.path.pardir)))

import argparse
from dataset import Dataset
from config import ALL_DATASET_NAMES, BIAS_DATA_PATH, ALL_MODEL_NAMES
from results import read_results_for, compute_metrics_for

parser = argparse.ArgumentParser(description="Assess the number of test predictions affected by a certain type of bias in a dataset")

parser.add_argument('--dataset',
                    choices=ALL_DATASET_NAMES,
                    help="Dataset in {}".format(ALL_DATASET_NAMES),
                    required=True)

parser.add_argument("--bias",
                    type=str,
                    choices=["1", "2", "3", "any"],
                    default="any",
                    help="The type of bias to analyze")

args = parser.parse_args()
bias_type = args.bias
dataset_name = args.dataset
d = Dataset(dataset_name)

data_bias_b1_filepath = os.path.join(BIAS_DATA_PATH, dataset_name + "_test_set_b1.csv")
data_bias_b2_filepath = os.path.join(BIAS_DATA_PATH, dataset_name + "_test_set_b2.csv")
data_bias_b3_filepath = os.path.join(BIAS_DATA_PATH, dataset_name + "_test_set_b3.csv")

test_fact_2_head_bias, test_fact_2_tail_bias = {}, {}

def _compute_test_fact_bias(type_of_bias: str):
    """
    Compute for each test triple in the dataset if it is prone to a specific type of bias
    :param type_of_bias: the type of bias to analyze. It must be either "1" or "2" or "3"
    :return: two maps:
                the 1st one associates each test fact to True if its head prediction is prone to bias, False otherwise
                the 2nd one associates each test fact to True if its tail prediction is prone to bias, False otherwise
    """
    _test_fact_2_head_bias, _test_fact_2_tail_bias = {}, {}

    if type_of_bias == "1":
        file_to_read = data_bias_b1_filepath
    elif type_of_bias == "2":
        file_to_read = data_bias_b2_filepath
    elif type_of_bias == "3":
        file_to_read = data_bias_b3_filepath
    else:
        raise ValueError("Method _compute_test_fact_bias only accepts bias type \"1\", or \"2\", or \"3\".")

    with open(file_to_read, "r") as infile:
        inlines = infile.readlines()
        for inline in inlines:
            head, rel, tail, head_bias_str, tail_bias_str = inline.strip().split(";")

            _head_bias = True if head_bias_str == "1" else False
            _tail_bias = True if tail_bias_str == "1" else False
            _test_fact_2_head_bias[(head, rel, tail)] = _head_bias
            _test_fact_2_tail_bias[(head, rel, tail)] = _tail_bias

    return _test_fact_2_head_bias, _test_fact_2_tail_bias

# if bias type is "1" or "2" or "3"
if bias_type in ["1", "2", "3"]:
    test_fact_2_head_bias, test_fact_2_tail_bias = _compute_test_fact_bias(bias_type)

# if bias type is "any"
else:
    test_fact_2_head_bias, test_fact_2_tail_bias = {}, {}
    test_fact_2_head_bias_1, test_fact_2_tail_bias_1 = _compute_test_fact_bias("1")
    test_fact_2_head_bias_2, test_fact_2_tail_bias_2 = _compute_test_fact_bias("2")
    test_fact_2_head_bias_3, test_fact_2_tail_bias_3 = _compute_test_fact_bias("3")

    for (h, r, t) in d.test_triples:
        test_fact_2_head_bias[(h, r, t)] = test_fact_2_head_bias_1[(h, r, t)] or \
                                           test_fact_2_head_bias_2[(h, r, t)] or \
                                           test_fact_2_head_bias_3[(h, r, t)]
        test_fact_2_tail_bias[(h, r, t)] = test_fact_2_tail_bias_1[(h, r, t)] or \
                                           test_fact_2_tail_bias_2[(h, r, t)] or \
                                           test_fact_2_tail_bias_3[(h, r, t)]


for model_name in ALL_MODEL_NAMES:
    all_ranks = []
    debiased_ranks = []
    test_fact_2_head_rank, test_fact_2_tail_rank = read_results_for(model_name, d)

    for test_fact in test_fact_2_head_rank:
        all_ranks.append(test_fact_2_head_rank[test_fact])
        all_ranks.append(test_fact_2_tail_rank[test_fact])

        if not test_fact_2_head_bias[test_fact]:
            debiased_ranks.append(test_fact_2_head_rank[test_fact])
        if not test_fact_2_tail_bias[test_fact]:
            debiased_ranks.append(test_fact_2_tail_rank[test_fact])

    original_h1, original_h10, original_mr, original_mrr = compute_metrics_for(all_ranks)
    debiased_h1, debiased_h10, debiased_mr, debiased_mrr = compute_metrics_for(debiased_ranks)

    if original_h1 != 0:
        difference_h1_percentage = round((debiased_h1 - original_h1) * 100 / original_h1, 1)
    else:
        difference_h1_percentage = "--"

    if original_h10 != 0:
        difference_h10_percentage = round((debiased_h10 - original_h10) * 100 / original_h10, 1)
    else:
        difference_h10_percentage = "--"

    difference_mr_percentage = round((debiased_mr - original_mr) * 100 / original_mr, 1)
    difference_mrr_percentage = round((debiased_mrr - original_mrr) * 100 / original_mrr, 1)

    print("\t" + model_name)
    print("\tOriginal predictions: " + str(2 * len(d.test_triples)) + "; unbiased: " + str(len(debiased_ranks)) + ")")
    print("\tOriginal H@1: " + str(original_h1) + ";\tde-biased H@1: " + str(debiased_h1) + ";\t(" + str(difference_h1_percentage) + "%)")
    print("\tOriginal H@10: " + str(original_h10) + ";\tde-biased H@10: " + str(debiased_h10) + ";\t(" + str(difference_h10_percentage) + "%)")
    print("\tOriginal MRR: " + str(original_mrr) + ";\tde-biased MRR: " + str(debiased_mrr) + ";\t(" + str(difference_mrr_percentage) + "%)")
    print("\tOriginal MR: " + str(original_mr) + ";\tde-biased MR: " + str(debiased_mr) + ";\t(" + str(difference_mr_percentage) + "%)\n")
