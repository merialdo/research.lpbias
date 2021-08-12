import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.abspath(__file__), os.path.pardir, os.path.pardir)))

from collections import defaultdict
from dataset import Dataset
from config import BIAS_DATA_PATH, WN18RR, WN18

outlines = []

for dataset_name in [WN18, WN18RR]:
    data = Dataset(dataset_name)
    print("Identifying test predictions with inverse relations in dataset " + dataset_name + "...")

    train_triples = data.train_triples
    test_triples = data.test_triples

    inverse_relations = set()
    relation_2_inverse = {}


    head_and_tail_2_relations = defaultdict(lambda: set())
    relation_2_count = defaultdict(lambda: 0)
    for (h, r, t) in train_triples:
        head_and_tail_2_relations[(h, t)].add(r)
        relation_2_count[r] += 1
    relation_2_other_relations_occurring_inverse_count = defaultdict(lambda: defaultdict(lambda: 0))


    for (h, r, t) in train_triples:
        # mark that number of times that any other_rel has appeared as the inverse of r
        for other_rel in head_and_tail_2_relations[(t, h)]:
            if other_rel == r:
                continue
            relation_2_other_relations_occurring_inverse_count[r][other_rel] += 1

    relation_2_best_candidate_inverse = defaultdict(lambda: defaultdict(lambda: 0))
    for relation in relation_2_other_relations_occurring_inverse_count:
        candidate_inverse_relations_with_counts = relation_2_other_relations_occurring_inverse_count[relation].items()
        candidate_inverse_relations_with_counts = sorted(candidate_inverse_relations_with_counts, key=lambda x: x[1], reverse=True)
        relation_2_best_candidate_inverse[relation] = candidate_inverse_relations_with_counts[0]


    for r1 in relation_2_best_candidate_inverse:
        for r2 in relation_2_best_candidate_inverse:
            if r1 == r2:
                continue

            if r1 in inverse_relations or r2 in inverse_relations:
                continue

            r1_count = relation_2_count[r1]
            r1_best_inverse_candidate = relation_2_best_candidate_inverse[r1][0]
            r1_best_inverse_candidate_count_with_r1 = relation_2_best_candidate_inverse[r1][1]

            r2_count = relation_2_count[r2]
            r2_best_inverse_candidate = relation_2_best_candidate_inverse[r2][0]
            r2_best_inverse_candidate_count_with_r2 = relation_2_best_candidate_inverse[r2][1]

            if r1_best_inverse_candidate != r2 or r2_best_inverse_candidate != r1:
                continue


            if r1_best_inverse_candidate_count_with_r1 / r1_count >= 0.75 and \
                r2_best_inverse_candidate_count_with_r2 / r2_count >= 0.75:
                inverse_relations.add(r1)
                inverse_relations.add(r2)
                relation_2_inverse[r1] = r2
                relation_2_inverse[r2] = r1


    def is_an_inverse_prediction(head, rel, tail):

        if rel in inverse_relations:
            inverse_rel = relation_2_inverse[rel]
            if (tail, inverse_rel, head) in data.train_triples_set:
                return True

        return False


    for (x, y, z) in test_triples:
        biased_head_prediction = is_an_inverse_prediction(x, y, z)
        biased_tail_prediction = is_an_inverse_prediction(x, y, z)

        biased_head_prediction_str = "0"
        if biased_head_prediction:
            biased_head_prediction_str = "1"

        biased_tail_prediction_str = "0"
        if biased_tail_prediction:
            biased_tail_prediction_str = "1"

        outlines.append(";".join([x, y, z, biased_head_prediction_str, biased_tail_prediction_str]) + "\n")

    output_path = os.path.join(BIAS_DATA_PATH, data.name + "_test_set_inverse.csv")
    with open(output_path, "w") as outfile:
        outfile.writelines(outlines)
    outlines = []