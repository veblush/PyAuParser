import sys
import unittest
import pyauparser

class TestLexer(unittest.TestCase):

    def setUp(self):
        self.grammar_operator = pyauparser.Grammar.load_file("data/operator.egt")
        self.grammar_group = pyauparser.Grammar.load_file("Data/group.egt")

    def test_operator(self):
        src = "1+2*(3/4)"
        dst = ""
        lexer = pyauparser.Lexer(self.grammar_operator)
        lexer.load_string(src)
        while True:
            token = lexer.read_token()
            if   token.symbol == self.grammar_operator.symbol_Error:
                raise Exception()
            elif token.symbol == self.grammar_operator.symbol_EOF:
                break
            dst += token.lexeme
        self.assertEqual(src, dst)

    def test_comment(self):
        lexer = pyauparser.Lexer(self.grammar_group)
        lexer.load_string(
            """
                a // Comment
                /* Block /* Comment "*/ b /* " */
                (* Block (* Comment2 *) " *) c
                [* " *] " [* *] *] d
            """)

        tokens = lexer.read_token_all()
        terminals = [t.lexeme for t in tokens if t.symbol.type == pyauparser.SymbolType.TERMINAL]
        self.assertEqual(terminals, [u'a', u'b', u'c', u'd'])

    def test_html(self):
        lexer = pyauparser.Lexer(self.grammar_group)
        lexer.load_string(
            """
                a=none, 
                b=
                <html>
                   <head>
                     <title>Some page</title>
                   </head>
                   </body>
                     This is a tad easier than concatenating a series of strings!
                   </body>
                </html>
            """)

        tokens = lexer.read_token_all()
        terminals = [t.lexeme for t in tokens if t.symbol.type == pyauparser.SymbolType.TERMINAL]
        self.assertEqual(terminals[:-1], [u'a', u'=', u'none', u',', u'b', u'='])
        self.assertEqual(terminals[-1][:6], "<html>")
        self.assertEqual(terminals[-1][-7:], "</html>")

if __name__ == '__main__':
    unittest.main()
