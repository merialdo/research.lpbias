import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.abspath(__file__), os.path.pardir, os.path.pardir)))

from collections import defaultdict
from dataset import Dataset
from config import BIAS_DATA_PATH, WN18RR

outlines = []

data = Dataset(WN18RR)

train_triples = data.train_triples
test_triples = data.test_triples

symmetric_relations = set()

head_and_tail_2_relations = defaultdict(lambda: set())
relation_2_count = defaultdict(lambda: 0)
for (h, r, t) in train_triples:
    head_and_tail_2_relations[(h, t)].add(r)
    relation_2_count[r] += 1

relation_to_symmetric_count = defaultdict(lambda:0)
for (h, r, t) in train_triples:
    # mark that number of times that any other_rel has appeared as the inverse of r
    if r in head_and_tail_2_relations[(t, h)]:
        relation_to_symmetric_count[r] += 1

for relation in relation_to_symmetric_count:
    if float(relation_to_symmetric_count[relation]) / float(relation_2_count[relation]) >= 0.75:
        symmetric_relations.add(relation)


def is_a_symmetric_prediction(head, rel, tail):
    if rel in symmetric_relations:
        if (tail, rel, head) in data.train_triples_set:
            return True
    return False

for (x, y, z) in test_triples:
    biased_head_prediction = is_a_symmetric_prediction(x, y, z)
    biased_tail_prediction = is_a_symmetric_prediction(x, y, z)

    biased_head_prediction_str = "0"
    if biased_head_prediction:
        biased_head_prediction_str = "1"

    biased_tail_prediction_str = "0"
    if biased_tail_prediction:
        biased_tail_prediction_str = "1"

    outlines.append(";".join([x, y, z, biased_head_prediction_str, biased_tail_prediction_str]) + "\n")

output_path = os.path.join(BIAS_DATA_PATH, data.name + "_test_set_symmetric.csv")
with open(output_path, "w") as outfile:
    outfile.writelines(outlines)
outlines = []