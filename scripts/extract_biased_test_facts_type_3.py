import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.abspath(__file__), os.path.pardir, os.path.pardir)))

from collections import defaultdict
from dataset import Dataset
from config import ALL_DATASET_NAMES, BIAS_DATA_PATH

outlines = []
for dataset_name in ALL_DATASET_NAMES:
    print(dataset_name)

    data = Dataset(dataset_name)

    train_triples = data.train_triples
    test_triples = data.test_triples

    # map each relation to the number of times that relation is used in the training set
    relation_2_count = defaultdict(lambda: 0)

    # map each head and tail to the relations connecting them
    head_and_tail_2_relations = defaultdict(lambda: set())

    # map each relation to the heads and tails that it connects
    relation_to_heads_and_tails = defaultdict(lambda: set())
    for (h, r, t) in train_triples:
        head_and_tail_2_relations[(h, t)].add(r)
        relation_to_heads_and_tails[r].add((h,t))
        relation_2_count[r] += 1

    relation_2_dominating_relations = defaultdict(lambda: set())
    for r1 in data.relations:
        r1_heads_and_tails = relation_to_heads_and_tails[r1]
        for r2 in data.relations:
            r1_r2_count = 0

            if r2 == r1:
                continue

            r2_heads_and_tails = relation_to_heads_and_tails[r2]

            for r1_head_and_tail in r1_heads_and_tails:
                if r1_head_and_tail in r2_heads_and_tails:
                    r1_r2_count += 1

            if float(r1_r2_count) / float(len(r2_heads_and_tails)) > 0.5:
                relation_2_dominating_relations[r1].add(r2)


    def is_a_biased_tail_prediction(head, relation, tail):

        dominating_relations = relation_2_dominating_relations[relation]

        for dominating_relation in dominating_relations:
            if (head, dominating_relation, tail) in data.train_triples_set:
                return True
        return False

    def is_a_biased_head_prediction(head, relation, tail):
        dominating_relations = relation_2_dominating_relations[relation]

        for dominating_relation in dominating_relations:
            if (head, dominating_relation, tail) in data.train_triples_set:
                return True
        return False

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

    output_path = os.path.join(BIAS_DATA_PATH, dataset_name + "_test_set_b3.csv")
    with open(output_path, "w") as outfile:
        outfile.writelines(outlines)
    outlines = []