import os
import sys
import pyauparser


def main():
    g = pyauparser.Grammar.load_file("data/operator.egt")

    # build a whole parse tree from string
    try:
        tree = pyauparser.parse_string_to_tree(g, "-2*(3+4)-5")
        tree.dump()
        print
    except pyauparser.ParseError as e:
        print e

    # evaluate a parse tree by traverse nodes
    def evaluate(node):
        r = lambda s: g.get_production(s).index
        h = {
            r('<E> ::= <E> + <M>'): lambda c: e(c[0]) + e(c[2]),
            r('<E> ::= <E> - <M>'): lambda c: e(c[0]) - e(c[2]),
            r('<E> ::= <M>'):       lambda c: e(c[0]),
            r('<M> ::= <M> * <N>'): lambda c: e(c[0]) * e(c[2]),
            r('<M> ::= <M> / <N>'): lambda c: e(c[0]) / e(c[2]),
            r('<M> ::= <N>'):       lambda c: e(c[0]),
            r('<N> ::= - <V>'):     lambda c: -e(c[1]),
            r('<N> ::= <V>'):       lambda c: e(c[0]),
            r('<V> ::= Num'):       lambda c: int(c[0].token.lexeme),
            r('<V> ::= ( <E> )'):   lambda c: e(c[1]),
        }
        def e(node):
            handler = h[node.production.index]
            return handler(node.childs)
        return e(node)

    result = evaluate(tree)
    print "Result = {0}".format(result)


if __name__ == "__main__":
    main()
