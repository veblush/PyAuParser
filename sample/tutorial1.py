import os
import sys
import pyauparser
from pyauparser.grammar import get_enum_name


def main():
    g = pyauparser.Grammar.load_file("data/operator.egt")

    # parse string and call handler at every parsing event
    # usually use reduce event for processing
    try:
        def callback(ret, arg):
            print "{0}\t{1}".format(
                get_enum_name(pyauparser.parser.ParseResultType, ret), arg)
        pyauparser.parse_string(g, "-2*(3+4)-5", handler=callback)
    except pyauparser.ParseError as e:
        print e

    # instead of handling parse events, create a whole parse
    # tree from string and use it for furthur processing,
    # which is convinient and powerful.
    try:
        tree = pyauparser.parse_string_to_tree(g, "-2*(3+4)-5")
        tree.dump()
    except pyauparser.ParseError as e:
        print e


if __name__ == "__main__":
    main()
