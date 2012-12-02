#!/usr/bin/python2

import os
import sys
import codecs
import pyauparser


def main():
    # tokenize an input string by lexer with grammar loaded
    # you can know how to use lexer manually

    g = pyauparser.Grammar.load_file("data/operator.egt")

    lexer = pyauparser.Lexer(g)
    lexer.load_file("data/operator_sample_1.txt")

    while True:
        token = lexer.read_token()
        print (token.symbol.name, token.lexeme, token.position)
        if   token.symbol.type == pyauparser.SymbolType.END_OF_FILE:
            break
        elif token.symbol.type == pyauparser.SymbolType.ERROR:
            print "ERROR({0}:{1}): Unknown Token '{0}'".format(
                token.position[0], token.position[1], token.lexeme)
            return

    print "done", lexer.position


if __name__ == "__main__":
    main()
