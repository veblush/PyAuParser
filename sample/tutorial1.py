import os
import sys
import pyauparser


def main():
    g = pyauparser.Grammar.load_file("data/operator.egt")

    # parse string and call handler at every parsing event
    # usually use reduce event for processing
    try:
        def callback(ret, p):
            if ret == pyauparser.parser.ParseResultType.SHIFT:
                print "Shift\t{0}".format(p.top)
            elif ret == pyauparser.parser.ParseResultType.REDUCE:
                print "Reduce\t{0}".format(p.reduction)
            elif ret == pyauparser.parser.ParseResultType.ACCEPT:
                print "Accept\t{0}".format(p.top)
            elif ret == pyauparser.parser.ParseResultType.ERROR:
                print "Error\t{0}".format(p.error_info)
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
