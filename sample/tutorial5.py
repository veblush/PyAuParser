import os
import sys
import pyauparser

# grammar_operator.py is generated as following.
# > auparser c data/operator.egt grammar_operator.py
import grammar_operator


def main():
    # with grammar_operator module,
    # a grammar instance could be constructed without any .egt file.
    g = grammar_operator.load()

    try:
        tree = pyauparser.parse_string_to_tree(g, "-2*(3+4)-5")
        tree.dump()
    except pyauparser.ParseError as e:
        print e


if __name__ == "__main__":
    main()
