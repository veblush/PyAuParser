#!/usr/bin/python2

import os
import sys
import pyauparser


def main():
    # parse an input string by parser with grammar loaded.
    # REDUCE event is a good starting point if you want to handle.

    g = pyauparser.Grammar.load_file("data/operator.egt")
    
    p = pyauparser.Parser(g)
    p.load_file("data/operator_sample_1.txt")
    #p.trim_reduction = True
    
    while True:
        ret = p.parse_step()
        if   ret == pyauparser.ParseResultType.ACCEPT:
            print "[Accept]"
            break
        elif ret == pyauparser.ParseResultType.SHIFT:
            token = p.token
            print "[Shift] {0} '{1}' ({2}:{3})".format(
                    token.symbol.name, token.lexeme,
                    token.position[0], token.position[1])
        elif ret == pyauparser.ParseResultType.REDUCE:
            print "[Reduce] {0}".format(p.reduction.production)
        elif ret == pyauparser.ParseResultType.REDUCE_ELIMINATED:
            print "[ReduceEliminated]"
        elif ret == pyauparser.ParseResultType.ERROR:
            print "[Error] {0}".format(p.error_info)
            return

    print "done", p.position


if __name__ == "__main__":
    main()
