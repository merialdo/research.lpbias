import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.abspath(__file__), os.path.pardir, os.path.pardir)))

import argparse
from dataset import Dataset
from config import ALL_DATASET_NAMES, BIAS_DATA_PATH
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

all_predictions = 2*len(d.test_triples)
debiased_predictions = 0

for (h, r, t) in d.test_triples:
    if test_fact_2_head_bias[(h, r, t)] is False:
        debiased_predictions+= 1
    if test_fact_2_tail_bias[(h, r, t)] is False:
        debiased_predictions+= 1

print("\tAll " + d.name + " test facts: " + str(len(d.test_triples)))
print("\tAll " + d.name + " test predictions: " + str(all_predictions))
print("\tTest predictions prone type \"" + bias_type + "\" bias: " + str(all_predictions-debiased_predictions))
print("\tTest predictions not prone to type \"" + bias_type + "\" bias: " + str(debiased_predictions) + " (" + str(round(float(debiased_predictions-all_predictions)/float(all_predictions)*100, 1)) + "%)")