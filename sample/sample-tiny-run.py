#!/usr/bin/python2

import os
import sys
import pyauparser


def evaluate(grammar, node):
    r = lambda s: grammar.get_production(s).index
    h = {
        r('<stmt seq> ::= <stmt seq> ; <stmt>'):
            lambda n, c: (e(c[0]), e(c[2])),
        r('<if stmt> ::= IF <exp> THEN <stmt seq> END'):
            lambda n, c: e(c[3]) if e(c[1]) else None,
        r('<if stmt> ::= IF <exp> THEN <stmt seq> ELSE <stmt seq> END'):
            lambda n, c: e(c[3]) if e(c[1]) else e(c[5]),
        r('<repeat stmt> ::= REPEAT <stmt seq> UNTIL <exp>'):
            lambda n, c: any((e(c[1]), e(c[3]))[1] is False
                             for x in xrange(100000)),
        r('<assign stmt> ::= ID := <exp>'):
            lambda n, c: vars.__setitem__(c[0].token.lexeme, e(c[2])),
        r('<read stmt> ::= READ ID'):
            lambda n, c: vars.__setitem__(c[1].token.lexeme,
                                          int(raw_input("? "))),
        r('<write stmt> ::= WRITE <exp>'):
            lambda n, c: write(e(c[1])),
        r('<exp> ::= <simple exp> < <simple exp>'):
            lambda n, c: e(c[0]) < e(c[2]),
        r('<exp> ::= <simple exp> = <simple exp>'):
            lambda n, c: e(c[0]) == e(c[2]),
        r('<simple exp> ::= <simple exp> + <term>'):
            lambda n, c: e(c[0]) + e(c[2]),
        r('<simple exp> ::= <simple exp> - <term>'):
            lambda n, c: e(c[0]) - e(c[2]),
        r('<term> ::= <term> * <factor>'):
            lambda n, c: e(c[0]) * e(c[2]),
        r('<term> ::= <term> / <factor>'):
            lambda n, c: e(c[0]) / e(c[2]),
        r('<factor> ::= ( <exp> )'):
            lambda n, c: e(c[1]),
        r('<factor> ::= Number'):
            lambda n, c: int(c[0].token.lexeme),
        r('<factor> ::= ID'):
            lambda n, c: vars.get(c[0].token.lexeme, None),
    }

    vars = {}

    def e(node):
        handler = h.get(node.production.index, None)
        if handler:
            return handler(node, node.childs)
        else:
            return e(node.childs[0])

    def write(v):
        print v

    e(node)


def main():
    grammar = pyauparser.Grammar.load_file("data/tiny.egt")

    def run(file):
        print "* RUN:", file
        try:
            tree = pyauparser.parse_file_to_tree(grammar, file)
        except pyauparser.ParseError as e:
            print e
            return False
        evaluate(grammar, tree)
        return True

    run("data/tiny_sample_1.txt")
    print
    run("data/tiny_sample_2.txt")

if __name__ == "__main__":
    main()
