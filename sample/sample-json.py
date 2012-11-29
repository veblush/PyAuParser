#!/usr/bin/python2

import os
import sys
import pyauparser
import pprint
import json


class JsonParser(object):
    def __init__(self):
        self.g = pyauparser.Grammar.load_file("data/json.egt")
        self.h = pyauparser.ProductionHandler({
            '<Json> ::= <Object>':                None,
            '<Json> ::= <Array>':                 None,
            '<Object> ::= { <Members> }':         lambda c: dict(c[1]),
            '<Object> ::= { }':                   lambda c: dict(),
            '<Members> ::= <Members> , <Member>': lambda c: c[0] + [c[2]],
            '<Members> ::= <Member>':             lambda c: [c[0]],
            '<Member> ::= String : <Value>':      lambda c: (c[0].lexeme[1:-1], c[2]),
            '<Array> ::= [ <Values> ]':           lambda c: c[1],
            '<Array> ::= [ ]':                    lambda c: [],
            '<Values> ::= <Values> , <Value>':    lambda c: c[0] + [c[2]],
            '<Values> ::= <Value>':               lambda c: [c[0]],
            '<Value> ::= <Object>':               None,
            '<Value> ::= <Array>':                None,
            '<Value> ::= Integer':                lambda c: int(c[0].lexeme),
            '<Value> ::= Float':                  lambda c: float(c[0].lexeme),
            '<Value> ::= String':                 lambda c: c[0].lexeme[1:-1],
            '<Value> ::= false':                  lambda c: False,
            '<Value> ::= null':                   lambda c: None,
            '<Value> ::= true':                   lambda c: True
        }, self.g)

    def parse(self, file_path):
        pyauparser.parse_file(self.g, file_path, encoding="utf-8", handler=self.h)
        return self.h.result


json_parser = JsonParser()
def load_json(file_path):
    return json_parser.parse(file_path)


def load_json_show_tree(file_path):
    g = pyauparser.Grammar.load_file("data/json.egt")
    g.get_production('<Object> ::= { <Members> }').sr_merge_child = True
    g.get_production('<Array> ::= [ <Values> ]').sr_merge_child = True
    pyauparser.parse_file_to_stree(g, file_path, encoding="utf-8").dump()


def main():
    file_path = "Data/JSON_sample_1.txt"

    print "***** json.loads *****"
    a = json.loads(open(file_path).read())
    pprint.pprint(a)
    print
    
    print "***** load_json *****"
    b = load_json(file_path)
    pprint.pprint(b)
    print

    print "***** load_json_show_tree *****"
    load_json_show_tree(file_path)
    print


if __name__ == "__main__":
    main()
