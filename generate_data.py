# # # Imports # # #

from __future__ import print_function  # assuming Python 2.7

import sys
from collections import Counter
from random import uniform, shuffle

try:
    from nltk.parse.generate import generate
    from nltk import CFG
except ImportError:
    sys.exit("You need NLTK to run the script: pip install nltk")

# # # Constants # # #

GRAMMAR_PATH = "./grammar"

# How many rule expansions to do while generating
RULE_APPLICATION_DEPTH = 10

# How many random sentences to produce
OUTPUT_SIZE = 2000

PREAMBLE = [
    "// The questions here are pre-generated.",
    "// See the Python script generate_data.py for details.",
    "let questions = [",
]

OUTPUT_PATH = "./random_questions_data.js"

# # # Functions # # #


def is_valid(sentence):
    # Drop non-questions
    if sentence[-1] != "?":
        return False
    # Avoid "lebayt", we say "habayta" instead
    for i, token in enumerate(sentence[:-2]):
        if token == "le_" and sentence[i + 1] == "bayt":
            return False
    c = Counter(sentence)
    # Avoid "po" and "kan" in the same sentence
    if "po" in c and "kan" in c:
        return False
    # Avoid repetitions of lexical (non-function) words
    for token in c:
        if c[token] > 1 and token not in {"be_", "mi_", "le_", "ve_"}:
            return False
    return True


def postprocess(sentence):
    return (
        " ".join(sentence)
        .replace("mi_ u", "meu")
        .replace("mi_ a", "mea")
        .replace("ve_ m", "um")
        .replace("ve_ b", "ub")
        .replace("ve_ v", "uv")
        .replace("ve_ p", "up")
        .replace("ve_ f", "uf")
        .replace("_ ", "")
        .replace(" ,", ",")
        .replace(" ?", "?")
        .replace("berechov", "birchov")
        .replace("lerechov", "lirchov")
        .replace("mirechov", "merechov")
    )


def to_js(sentences):
    return "\n".join(PREAMBLE + ['  "%s",' % s for s in sentences] + ["];"])


def main():
    with open(GRAMMAR_PATH) as f:
        grammar = CFG.fromstring(f.read().strip())

    filtered = filter(is_valid, generate(grammar, depth=RULE_APPLICATION_DEPTH))
    postprocessed = map(postprocess, filtered)
    all_output = list(set(postprocessed))

    # Favor shorter sentences while sampling
    scores = [uniform(0, 1) / (len(s) ** 0.3) for s in all_output]
    limit = sorted(scores)[-OUTPUT_SIZE]
    sampled_output = [all_output[i] for i, score in enumerate(scores) if score >= limit]
    shuffle(sampled_output)

    with open(OUTPUT_PATH, "w") as f:
        f.write(to_js(sampled_output))


# # # Main loop # # #

if __name__ == "__main__":
    main()
