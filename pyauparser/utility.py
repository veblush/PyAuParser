import os
import sys
import parser
import tree


class ParseError(Exception):
    def __init__(self, error_info):
        self.error_info = error_info

    def __str__(self):
        return str(self.error_info)


def parse_file(grammar, file_or_path, encoding=None, handler=None):
    p = parser.Parser(grammar)
    p.load_file(file_or_path, encoding)
    if p.parse_all(handler) != parser.ParseResultType.ACCEPT:
        raise ParseError(p.error_info)


def parse_string(grammar, s, encoding=None, handler=None):
    p = parser.Parser(grammar)
    p.load_string(s)
    if p.parse_all(handler) != parser.ParseResultType.ACCEPT:
        raise ParseError(p.error_info)


def parse_file_to_tree(grammar, file_or_path, encoding=None):
    p = parser.Parser(grammar)
    p.load_file(file_or_path, encoding)
    builder = tree.TreeBuilder()
    if p.parse_all(builder) == parser.ParseResultType.ACCEPT:
        return builder.result
    else:
        raise ParseError(p.error_info)


def parse_string_to_tree(grammar, s, encoding=None):
    p = parser.Parser(grammar)
    p.load_string(s)
    builder = tree.TreeBuilder()
    if p.parse_all(builder) == parser.ParseResultType.ACCEPT:
        return builder.result
    else:
        raise ParseError(p.error_info)


def parse_file_to_stree(grammar, file_or_path, encoding=None):
    p = parser.Parser(grammar)
    p.load_file(file_or_path, encoding)
    builder = tree.SimplifiedTreeBuilder()
    if p.parse_all(builder) == parser.ParseResultType.ACCEPT:
        return builder.result
    else:
        raise ParseError(p.error_info)


def parse_string_to_stree(grammar, s, encoding=None):
    p = parser.Parser(grammar)
    p.load_string(s)
    builder = tree.SimplifiedTreeBuilder()
    if p.parse_all(builder) == parser.ParseResultType.ACCEPT:
        return builder.result
    else:
        raise ParseError(p.error_info)
