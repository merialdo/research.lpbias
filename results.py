import html
import os

import numpy

from config import RESULTS_PATH, ANYBURL
from dataset import Dataset


def read_results_for(model_name: str,
                     dataset: Dataset):

    filepath = os.path.join(RESULTS_PATH, dataset.name, model_name, model_name.lower()+ "_filtered_ranks.csv")
    if model_name == ANYBURL:
        filepath = os.path.join(RESULTS_PATH, dataset.name, model_name, model_name.lower() + "_filtered_ranks.csv")

    test_fact_2_head_rank = {}
    test_fact_2_tail_rank = {}

    with open(filepath, "r") as infile:
        lines = infile.readlines()
        for line in lines:
            head, rel, tail, hrank_str, trank_str = line.strip().split(";")

            if hrank_str.startswith("MISS_"):
                hrank = int((float(hrank_str.replace("MISS_", "")) + dataset.num_entities)/2)
            else:
                hrank = int(float(hrank_str))

            if trank_str.startswith("MISS_"):
                trank = int((float(trank_str.replace("MISS_", "")) + dataset.num_entities)/2)
            else:
                trank = int(float(trank_str))

            head = html.unescape(head.lower().replace(",", "").replace(":", ""))
            rel = html.unescape(rel.lower().replace(",", "").replace(":", ""))
            tail = html.unescape(tail.lower().replace(",", "").replace(":", ""))

            test_fact_2_head_rank[(head, rel, tail)] = hrank
            test_fact_2_tail_rank[(head, rel, tail)] = trank

    return test_fact_2_head_rank, test_fact_2_tail_rank


def compute_metrics_for(ranks):
    count_rank_1 = 0
    count_rank_10 = 0

    reciprocal_ranks = []
    for r in ranks:
        reciprocal_ranks.append(1.0/float(r))
        if r <= 10:
            count_rank_10 += 1
            if r == 1:
                count_rank_1 += 1

    h1 = float(count_rank_1)/float(len(ranks))
    h10 = float(count_rank_10)/float(len(ranks))
    mr = numpy.average(ranks)
    mrr = numpy.average(reciprocal_ranks)

    return h1, h10, mr, mrr