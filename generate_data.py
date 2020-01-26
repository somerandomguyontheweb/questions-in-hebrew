# # # Imports # # #

from __future__ import print_function  # assuming Python 2.7

import sys
from collections import Counter, defaultdict as dd
from random import choice

# # # Constants # # #

GRAMMAR_PATH = "./grammar"

INITIAL_SYMBOL = "S"

# How many random sentences to produce
OUTPUT_SIZE = 2000

PREAMBLE = [
    "// The questions here are pre-generated.",
    "// See the Python script generate_data.py for details.",
    "let questions = [",
]

OUTPUT_PATH = "./random_questions_data.js"

# # # Functions # # #


is_nonterminal = lambda s: s.upper() == s and s[0] != "'" and s[-1] != "'"
is_terminal = lambda s: s[0] == s[-1] == "'"


def load_grammar(path):
    # This function assumes the grammar to be syntactically well-formed
    with open(path) as f:
        rules = f.read().strip().split("\n")
    grammar = dd(list)
    for rule in rules:
        assert " -> " in rule
        lhs, rhs = rule.split(" -> ")
        expansions = rhs.split(" | ")
        for e in expansions:
            grammar[lhs].append(e.split(" "))
    # Verify that the grammar is meaningful
    assert INITIAL_SYMBOL in grammar, (
        "Initial symbol %s not in grammar" % INITIAL_SYMBOL
    )
    for lhs in grammar:
        for e in grammar[lhs]:
            for symbol in e:
                assert is_nonterminal(symbol) or is_terminal(symbol), (
                    "Invalid symbol: %s" % symbol
                )
                if is_nonterminal(symbol):
                    assert symbol in grammar, "Nonterminal not in grammar: %s" % symbol
                else:
                    assert symbol not in grammar, "Terminal expanded: %s" % symbol
    return grammar


expand_randomly = lambda s, grammar: [s] if s not in grammar else choice(grammar[s])


def generate_random_sentence(grammar):
    expansion = [INITIAL_SYMBOL]
    while any(is_nonterminal(s) for s in expansion):
        expansion = [s_new for s in expansion for s_new in expand_randomly(s, grammar)]
    return [s[1:-1] for s in expansion]


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
    # Avoid "bayt" and "habayta" in the same sentence
    if "bayt" in c and "habayta" in c:
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
    grammar = load_grammar(GRAMMAR_PATH)
    sampled_output = set()
    while len(sampled_output) < OUTPUT_SIZE:
        sentence = generate_random_sentence(grammar)
        if is_valid(sentence):
            sampled_output.add(postprocess(sentence))

    with open(OUTPUT_PATH, "w") as f:
        f.write(to_js(sampled_output))


# # # Main loop # # #

if __name__ == "__main__":
    main()
