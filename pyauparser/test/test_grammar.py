import sys
import unittest
import codecs
import StringIO
import pyauparser

class TestGrammar(unittest.TestCase):

    def setUp(self):
        self.grammar = pyauparser.Grammar.load_file("Data/operator.egt")

    def test_load(self):
        self.assertEqual(len(self.grammar.properties), 8)
        self.assertEqual(len(self.grammar.charsets), 10)
        self.assertEqual(len(self.grammar.symbols), 14)
        self.assertEqual(len(self.grammar.symbolgroups), 0)
        self.assertEqual(len(self.grammar.productions), 10)
        self.assertEqual(len(self.grammar.dfastates), 11)
        self.assertEqual(len(self.grammar.lalrstates), 19)

    def test_export(self):
        with open("temp_operator_grammar.py", "wb") as f:
            self.grammar.export_to_py(f)
        import temp_operator_grammar
        grammar2 = temp_operator_grammar.load()
        gf1 = StringIO.StringIO()
        self.grammar.export_to_txt(gf1)
        gf2 = StringIO.StringIO()
        grammar2.export_to_txt(gf2)
        self.assertEqual(gf1.getvalue(), gf2.getvalue())

if __name__ == '__main__':
    unittest.main()
