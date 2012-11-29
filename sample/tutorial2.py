import os
import sys
import pyauparser


def main():
    g = pyauparser.Grammar.load_file("data/operator.egt")

    # every production has a lambda handler which evaluates value from childs.
    # Because LALR is a bottom-up parser, handler would be called from bottom.
    h = pyauparser.ProductionHandler({
        '<E> ::= <E> + <M>': lambda c: c[0] + c[2],
        '<E> ::= <E> - <M>': lambda c: c[0] - c[2],
        '<E> ::= <M>':       lambda c: c[0],
        '<M> ::= <M> * <N>': lambda c: c[0] * c[2],
        '<M> ::= <M> / <N>': lambda c: c[0] / c[2],
        '<M> ::= <N>':       lambda c: c[0],
        '<N> ::= - <V>':     lambda c: -c[1],
        '<N> ::= <V>':       lambda c: c[0],
        '<V> ::= Num':       lambda c: int(c[0].lexeme),
        '<V> ::= ( <E> )':   lambda c: c[1],
    }, g)

    try:
        pyauparser.parse_string(g, "-2*(3+4)-5", handler=h)
        print "Result = {0}".format(h.result)
    except pyauparser.ParseError as e:
        print e


if __name__ == "__main__":
    main()
