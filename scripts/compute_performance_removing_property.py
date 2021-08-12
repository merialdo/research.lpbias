import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.abspath(__file__), os.path.pardir, os.path.pardir)))

import argparse
from dataset import Dataset
from config import BIAS_DATA_PATH, ALL_MODEL_NAMES, WN18, WN18RR
from results import read_results_for, compute_metrics_for

parser = argparse.ArgumentParser(description="Assess the number of test predictions affected by a certain type of bias in a dataset")

parser.add_argument('--dataset',
                    choices=[WN18, WN18RR],
                    help="Dataset in {}".format([WN18, WN18RR]),
                    required=True)

parser.add_argument("--property",
                    type=str,
                    choices=["inverse", "symmetric", "any"],
                    default="any",
                    help="The type of relation property to analyze")

args = parser.parse_args()
rel_property = args.property
dataset_name = args.dataset
d = Dataset(dataset_name)

test_set_inverse_filepath = os.path.join(BIAS_DATA_PATH, dataset_name + "_test_set_inverse.csv")
test_set_symmetric_filepath = os.path.join(BIAS_DATA_PATH, dataset_name + "_test_set_symmetric.csv")

def _compute_affected_test_facts(property):
    """
    Compute for each test triple in the dataset if it is affected by a specific relation property
    :param property: the relation property to analyze. It must be either "inverse" or "symmetric"
    :return: two maps:
                the 1st one associates each test fact to True if its head prediction is affected, False otherwise
                the 2nd one associates each test fact to True if its tail prediction is affected, False otherwise
    """
    _test_fact_2_head_affected, _test_fact_2_tail_affected = {}, {}

    if property == "inverse":
        file_to_read = test_set_inverse_filepath
    elif property == "symmetric":
        file_to_read = test_set_symmetric_filepath
    else:
        raise ValueError("Method _compute_affected_test_facts only accepts properties \"inverse\" or \"symmetric\"")

    with open(file_to_read, "r") as infile:
        inlines = infile.readlines()
        for inline in inlines:
            head, rel, tail, head_affected_str, tail_affected_str = inline.strip().split(";")
            head_affected = True if head_affected_str == "1" else False
            tail_affected = True if tail_affected_str == "1" else False
            _test_fact_2_head_affected[(head, rel, tail)] = head_affected
            _test_fact_2_tail_affected[(head, rel, tail)] = tail_affected

    return _test_fact_2_head_affected, _test_fact_2_tail_affected

# if rel_property is "inverse" or "symmetric"
if rel_property in ["inverse", "symmetric"]:
    test_fact_2_head_affected, test_fact_2_tail_affected = _compute_affected_test_facts(rel_property)

# if rel_property is "any"
else:
    test_fact_2_head_affected, test_fact_2_tail_affected = {}, {}

    test_fact_2_head_affected_inv, test_fact_2_tail_affected_inv = _compute_affected_test_facts("inverse")
    test_fact_2_head_affected_symm, test_fact_2_tail_affected_symm = _compute_affected_test_facts("symmetric")

    for (h, r, t) in d.test_triples:
        test_fact_2_head_affected[(h, r, t)] = test_fact_2_head_affected_inv[(h, r, t)] or \
                                               test_fact_2_head_affected_symm[(h, r, t)]
        test_fact_2_tail_affected[(h, r, t)] = test_fact_2_tail_affected_inv[(h, r, t)] or \
                                               test_fact_2_tail_affected_symm[(h, r, t)]

for model_name in ALL_MODEL_NAMES:
    all_ranks = []
    unaffected_ranks = []
    test_fact_2_head_rank, test_fact_2_tail_rank = read_results_for(model_name, d)

    for test_fact in test_fact_2_head_rank:
        all_ranks.append(test_fact_2_head_rank[test_fact])
        all_ranks.append(test_fact_2_tail_rank[test_fact])

        if not test_fact_2_head_affected[test_fact]:
            unaffected_ranks.append(test_fact_2_head_rank[test_fact])
        if not test_fact_2_tail_affected[test_fact]:
            unaffected_ranks.append(test_fact_2_tail_rank[test_fact])

    original_h1, original_h10, original_mr, original_mrr = compute_metrics_for(all_ranks)
    unaffected_h1, unaffected_h10, unaffected_mr, unaffected_mrr = compute_metrics_for(unaffected_ranks)

    if original_h1 != 0:
        difference_h1_percentage = round((unaffected_h1 - original_h1) * 100 / original_h1, 1)
    else:
        difference_h1_percentage = "--"

    if original_h10 != 0:
        difference_h10_percentage = round((unaffected_h10 - original_h10) * 100 / original_h10, 1)
    else:
        difference_h10_percentage = "--"

    difference_mr_percentage = round((unaffected_mr - original_mr) * 100 / original_mr, 1)
    difference_mrr_percentage = round((unaffected_mrr - original_mrr) * 100 / original_mrr, 1)

    print("\t" + model_name)
    print("\tOriginal predictions: " + str(2 * len(d.test_triples)) + "; unaffected: " + str(len(unaffected_ranks)) + ")")
    print("\tOriginal H@1: " + str(original_h1) + ";\tNew H@1: " + str(unaffected_h1) + ";\t(" + str(difference_h1_percentage) + "%)")
    print("\tOriginal H@10: " + str(original_h10) + ";\tNew H@10: " + str(unaffected_h10) + ";\t(" + str(difference_h10_percentage) + "%)")
    print("\tOriginal MRR: " + str(original_mrr) + ";\tNew MRR: " + str(unaffected_mrr) + ";\t(" + str(difference_mrr_percentage) + "%)")
    print("\tOriginal MR: " + str(original_mr) + ";\tNew MR: " + str(unaffected_mr) + ";\t(" + str(difference_mr_percentage) + "%)\n")