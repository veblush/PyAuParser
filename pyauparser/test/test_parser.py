import sys
import unittest
import pyauparser

class TestParser(unittest.TestCase):

    def setUp(self):
        self.grammar = pyauparser.Grammar.load_file("data/operator.egt")

    def test_reduce(self):
        parser = pyauparser.Parser(self.grammar)
        parser.load_string("-(1+2)-3*4")

        reduce_rules = []
        while True:
            ret = parser.parse_reduce()
            if ret == pyauparser.ParseResultType.REDUCE:
                reduce_rules.append(parser.reduction.production.index)
            elif ret == pyauparser.ParseResultType.ACCEPT:
                break
            else:
                self.fail(parser.error_info)
                return

        def rule(s):
            return self.grammar.get_production(s).index
        check_rules = [
            rule("<V> ::= Num"),
            rule("<N> ::= <V>"),
            rule("<M> ::= <N>"),
            rule("<E> ::= <M>"),
            rule("<V> ::= Num"),
            rule("<N> ::= <V>"),
            rule("<M> ::= <N>"),
            rule("<E> ::= <E> + <M>"),
            rule("<V> ::= ( <E> )"),
            rule("<N> ::= - <V>"),
            rule("<M> ::= <N>"),
            rule("<E> ::= <M>"),
            rule("<V> ::= Num"),
            rule("<N> ::= <V>"),
            rule("<M> ::= <N>"),
            rule("<V> ::= Num"),
            rule("<N> ::= <V>"),
            rule("<M> ::= <M> * <N>"),
            rule("<E> ::= <E> - <M>")]
        
        self.assertEqual(reduce_rules, check_rules)

    def test_trim_reduce(self):
        parser = pyauparser.Parser(self.grammar)
        parser.load_string("-(1+2)-3*4")
        parser.trim_reduction = True

        reduce_rules = []
        while True:
            ret = parser.parse_reduce()
            if ret == pyauparser.ParseResultType.REDUCE:
                reduce_rules.append(parser.reduction.production.index)
            elif ret == pyauparser.ParseResultType.ACCEPT:
                break
            else:
                self.fail(parser.error_info)
                return

        def rule(s):
            return self.grammar.get_production(s).index
        check_rules = [
            rule("<V> ::= Num"),
            rule("<V> ::= Num"),
            rule("<E> ::= <E> + <M>"),
            rule("<V> ::= ( <E> )"),
            rule("<N> ::= - <V>"),
            rule("<V> ::= Num"),
            rule("<V> ::= Num"),
            rule("<M> ::= <M> * <N>"),
            rule("<E> ::= <E> - <M>")]
        
        self.assertEqual(reduce_rules, check_rules)

if __name__ == '__main__':
    unittest.main()
