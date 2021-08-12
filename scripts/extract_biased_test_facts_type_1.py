import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.abspath(__file__), os.path.pardir, os.path.pardir)))

from collections import defaultdict
from dataset import Dataset
from config import ALL_DATASET_NAMES, BIAS_DATA_PATH

THRESHOLD = 0.75

outlines = []
for dataset_name in ALL_DATASET_NAMES:
    print(dataset_name)

    data = Dataset(dataset_name)

    train_triples = data.train_triples
    test_triples = data.test_triples

    # map each relation to the number of times that relation is used in the training set
    relation_2_count = defaultdict(lambda: 0)

    # map each relation to the number of times any entity is used as head in train facts with that relation
    relation_2_head_counts = defaultdict(lambda: defaultdict(lambda: 0))

    # map each relation to the number of times any entity is used as tail in train facts with that relation
    relation_2_tail_counts = defaultdict(lambda: defaultdict(lambda: 0))

    for (h, r, t) in train_triples:
        relation_2_head_counts[r][h] += 1
        relation_2_tail_counts[r][t] += 1
        relation_2_count[r] += 1

    def is_a_biased_tail_prediction(head, relation, tail):
        return float(relation_2_tail_counts[relation][tail]) / float(relation_2_count[relation]) >= 0.75

    def is_a_biased_head_prediction(head, relation, tail):
        return float(relation_2_head_counts[relation][head]) / float(relation_2_count[relation]) >= 0.75


    for (x, y, z) in test_triples:
        biased_head_prediction = is_a_biased_head_prediction(x, y, z)
        biased_tail_prediction = is_a_biased_tail_prediction(x, y, z)

        biased_head_prediction_str = "0"
        if biased_head_prediction:
            biased_head_prediction_str = "1"

        biased_tail_prediction_str = "0"
        if biased_tail_prediction:
            biased_tail_prediction_str = "1"

        outlines.append(";".join([x, y, z, biased_head_prediction_str, biased_tail_prediction_str]) + "\n")

    output_path = os.path.join(BIAS_DATA_PATH, dataset_name + "_test_set_b1.csv")
    with open(output_path, "w") as outfile:
        outfile.writelines(outlines)
    outlines = []