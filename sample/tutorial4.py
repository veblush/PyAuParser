import os
import sys
import pyauparser


def main():
    g = pyauparser.Grammar.load_file("data/operator.egt")

    # set following production as a formatting one,
    # it makes that specified productions will be removed when
    # building a simplified tree if possible
    g.get_production('<V> ::= ( <E> )').sr_forward_child = True

    # build a whole simplified tree from string and dump it
    try:
        tree = pyauparser.parse_string_to_stree(g, "-2*(1+2+4)-2-2-1")
        tree.dump()
        print
    except pyauparser.ParseError as e:
        print e
        return

    # evaluate a simplified tree by traverse nodes
    def evaluate(node):
        r = lambda s: g.get_production(s).index
        h = {
            r('<E> ::= <E> + <M>'):
                lambda c: reduce(lambda x, y: x + y, (e(d) for d in c)),
            r('<E> ::= <E> - <M>'):
                lambda c: reduce(lambda x, y: x - y, (e(d) for d in c)),
            r('<M> ::= <M> * <N>'):
                lambda c: reduce(lambda x, y: x * y, (e(d) for d in c)),
            r('<M> ::= <M> / <N>'):
                lambda c: reduce(lambda x, y: x / y, (e(d) for d in c)),
            r('<N> ::= - <V>'):
                lambda c: -e(c[0]),
        }
        def e(node):
            if node.token:
                return int(node.token.lexeme)
            else:
                handler = h.get(node.production.index, None)
                return handler(node.childs) if handler else e(node.childs[0])
        return e(node)

    result = evaluate(tree)
    print "Result = {0}".format(result)


if __name__ == "__main__":
    main()
