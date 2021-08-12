import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.abspath(__file__), os.path.pardir, os.path.pardir)))

from collections import defaultdict
from dataset import Dataset, MANY_TO_ONE, ONE_TO_MANY, MANY_TO_MANY
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

    relation_2_heads = defaultdict(lambda: set())
    relation_2_tails = defaultdict(lambda: set())
    relation_and_head_2_tails = defaultdict(lambda: set())
    relation_and_tail_2_heads = defaultdict(lambda: set())


    for (h, r, t) in train_triples:
        relation_2_heads[r].add(h)
        relation_2_tails[r].add(t)
        relation_and_head_2_tails[(r, h)].add(t)
        relation_and_tail_2_heads[(r, t)].add(h)
        relation_2_count[r] += 1

    def is_a_biased_tail_prediction(head, relation, tail):
        if data.relation_2_type[relation] in [ONE_TO_MANY, MANY_TO_MANY]:

            #let's say the passed fact is <Barack Obama, speaks_language, English>

            # select the entities that are seen as heads in facts with the relation
            # e.g. <A, speaks_language, any_language>
            heads_involved_with_relation = relation_2_heads[relation]

            # select the entities that are seen as heads in facts <_, relation, tail>
            # e.g. <A, speaks_language, English>
            heads_involved_with_relation_and_tail = relation_and_tail_2_heads[(relation, tail)]

            assert len(heads_involved_with_relation_and_tail) <= len(heads_involved_with_relation)
            # the idea is that if most A entities that speak any language speak English too, then there is a bias
            return float(len(heads_involved_with_relation_and_tail)) / float(len(heads_involved_with_relation)) >= 0.5
        return False

    def is_a_biased_head_prediction(head, relation, tail):
        if data.relation_2_type[relation] in [MANY_TO_ONE, MANY_TO_MANY]:
            #let's say the passed fact is <USA, contain, Washington>

            # select the entities that are seen as tails in facts with the relation
            # e.g. <any_location, contains, A>
            tails_involved_with_relation = relation_2_tails[relation]

            # select the entities that are seen as tails in facts <head, relation, _>
            # e.g. <Washington, contain, A>
            tails_involved_with_relation_and_head = relation_and_head_2_tails[(relation, head)]

            # the idea is that if most A entities that are contained in a location are contained in USA too, there is a bias
            return float(len(tails_involved_with_relation_and_head)) / float(len(tails_involved_with_relation)) >= 0.5
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

    output_path = os.path.join(BIAS_DATA_PATH, dataset_name + "_test_set_b2.csv")
    with open(output_path, "w") as outfile:
        outfile.writelines(outlines)
    outlines = []