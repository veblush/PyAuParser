#!/usr/bin/python2

import os
import sys
import pyauparser


def main():
    g = pyauparser.Grammar.load_file("data/list.egt")

    g.get_production('<List> ::= [ <List1> ]').sr_merge_child =-True
    g.get_production('<List> ::= { <List2> }').sr_merge_child =-True

    print "********** TreeBuilder [a,b,c] **********"
    pyauparser.parse_string_to_tree(g, "[a,b,c]").dump()
    print

    print "********** SimplifiedTreeBuilder [a,b,c] **********"
    pyauparser.parse_string_to_stree(g, "[a,b,c]").dump()
    print

    print "********** TreeBuilder {a;b;c;} **********"
    pyauparser.parse_string_to_tree(g, "{a;b;c;}").dump()
    print

    print "********** SimplifiedTreeBuilder {a;b;c;} **********"
    pyauparser.parse_string_to_stree(g, "{a;b;c;}").dump()
    print


if __name__ == "__main__":
    main()
