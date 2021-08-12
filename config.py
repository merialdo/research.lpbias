import os

ROOT = os.path.realpath(os.path.join(os.path.abspath(__file__), ".."))
DATA_PATH = os.path.join(ROOT, "data")
BIAS_DATA_PATH = os.path.join(ROOT, "bias_data")
RESULTS_PATH = os.path.join(ROOT, "comparative_analysis_results")

# model names
ANALOGY = "ANALOGY"
ANYBURL = "AnyBURL-RE"
CAPSE = "CapsE"
COMPLEX = "ComplEx"
CONVE = "ConvE"
CONVKB = "ConvKB"
CONVR = "ConvR"
CROSSE = "CrossE"
DISTMULT = "DistMult"
HAKE = "HAKE"
HOLE = "HolE"
INTERACTE = "InteractE"
ROTATE = "RotatE"
RSN = "RSN"
SIMPLE = "SimplE"
STRANSE = "STransE"
TORUSE = "TorusE"
TRANSE = "TransE"
TUCKER = "TuckER"

ALL_MODEL_NAMES = [DISTMULT, COMPLEX, ANALOGY, SIMPLE, HOLE, TUCKER,
                   TRANSE, STRANSE, CROSSE, TORUSE, ROTATE, HAKE,
                   CONVE, CONVKB, CONVR, INTERACTE, CAPSE, RSN,
                   ANYBURL]

SELECTED_MODEL_NAMES = [COMPLEX, TUCKER,
                        TRANSE, CROSSE, HAKE,
                        INTERACTE, CAPSE, RSN,
                        ANYBURL]

# dataset names
FB15K = "FB15k"
FB15K_237 = "FB15k-237"
WN18 = "WN18"
WN18RR = "WN18RR"
YAGO3_10 = "YAGO3-10"
ALL_DATASET_NAMES = [FB15K, FB15K_237, WN18, WN18RR, YAGO3_10]