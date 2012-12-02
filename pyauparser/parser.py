import os
import sys
import grammar
from grammar import SymbolType, LALRActionType
from lexer import Lexer, Token


class ParseResultType:
    ACCEPT = 1
    SHIFT = 2
    REDUCE = 3
    REDUCE_ELIMINATED = 4
    ERROR = 5


class ParseItem(object):
    """ParseItem is an entity stored in a LALR stack.
       It holds a LALR state and value which is a token or
       a production related with shift or reduce process.
       Optionally it could have data that is a storage
       for a bottom-up evaluation.
    """

    def __init__(self, state, production=None, token=None):
        self.state = state              # grammar.LALRState
        self.production = production    # grammar.Production
        self.token = token              # lexer.Token
        self.data = None                # for saving an user-value

    def __str__(self):
        if self.production:
            return "S={0}, P={1}".format(self.state.index, self.production)
        elif self.token:
            return "S={0}, T={1}".format(self.state.index, self.token)
        else:
            return "S={0}".format(self.state.index)


class ParseErrorType:
    LEXICAL_ERROR = 1
    SYNTAX_ERROR = 2
    INTERNAL_ERROR = 3


class ParseErrorInfo(object):
    def __init__(self, type, position, state, token, expected_symbols):
        self.type = type
        self.position = position
        self.state = state
        self.token = token
        self.expected_symbols = expected_symbols

    def __str__(self):
        if   self.type == ParseErrorType.LEXICAL_ERROR:
            return "LexicalError({0}:{1}) Token='{1}'".format(
                self.token.position[0], self.token.position[1],
                self.token.lexeme)
        elif self.type == ParseErrorType.SYNTAX_ERROR:
            return "SyntaxError({0}:{1}) Token={1} '{2}' ExpectedTokens=[{3}]".format(
                self.token.position[0], self.token.position[1],
                self.token.symbol.name, self.token.lexeme,
                " ,".join([s.name for s in self.expected_symbols]))
        else:
            return "InternalError({0}:{1}) State={1}".format(
                self.position[0], self.position[1], self.state.index)


class Reduction(object):
    """Reduction is a result by a reduction step of parsing.
       It contains a reduced production rule, derived head and handles.
    """

    def __init__(self, production, head, handles):
        self.production = production
        self.head = head
        self.handles = handles

    def __str__(self):
        return "P={0}, H=({1}), Hs=[{2}]".format(
            self.production.index, self.head,
            ", ".join("({0})".format(h) for h in self.handles))


class ProductionHandler(object):
    """Simple handler for evaluation parse tree.
       It contains a dict of production-rule to handler.
       In parsing, every reduce events invoke __call__
       and a corresponding handler is called.
    """

    def __init__(self, handler_map, grammar=None):
        if grammar:
            # If a grammar is provided, a key of handler_map could be string.
            # String keys will be resolve to index as following.
            self.handler_map = {}
            for k, v in handler_map.iteritems():
                if isinstance(k, str) or isinstance(k, unicode):
                    rule = grammar.get_production(k).index
                    self.handler_map[rule] = v
                else:
                    self.handler_map[k] = v
        else:
            self.handler_map = handler_map
        self.result = None

    def __call__(self, ret, arg):
        if ret == ParseResultType.REDUCE:
            childs = [(h.data if h.production else h.token) for h in arg.handles]
            handler = self.handler_map.get(arg.production.index, None)
            if handler:
                arg.head.data = handler(childs)
            else:
                arg.head.data = childs[0]

        elif ret == ParseResultType.ACCEPT:
            self.result = arg.data


class Parser(object):
    """Main class for parsing which provides a parsing feature by using Lexer
       and LALR states in a grammar.
    """

    def __init__(self, grammar):
        self.grammar = grammar
        self.trim_reduction = False

    def load_lexer(self, lexer):
        self.lexer = lexer
        self.state = self.grammar.lalrinit
        self.stack = [ParseItem(self.state), ]
        self.token = Token(None, "", None)
        self.token_used = True
        self.error_info = None
        self.reduction = None

    def load_file(self, file_or_path, encoding=None):
        lexer = Lexer(self.grammar)
        lexer.load_file(file_or_path, encoding)
        self.load_lexer(lexer)

    def load_string(self, s):
        lexer = Lexer(self.grammar)
        lexer.load_string(s)
        self.load_lexer(lexer)

    def _read_token(self):
        while True:
            token = self.lexer.read_token()
            if token.symbol.type != SymbolType.NOISE:
                return token

    @property
    def line(self):
        return self.lexer.line

    @property
    def column(self):
        return self.lexer.column

    @property
    def position(self):
        return self.lexer.position

    @property
    def top(self):
        return self.stack[-1]

    def parse_step(self):
        """ Perform 1 step parsing which is one of shift, reduce, accept, error.
            If you are familar with shift-reduce parsing,
            it is a function that you're finding.
        """
        if self.token_used:
            self.token = self._read_token()
            self.token_used = False

        if self.token.symbol.type == SymbolType.ERROR:
            # Tokenizer error_info
            self.error_info = ParseErrorInfo(ParseErrorType.LEXICAL_ERROR,
                                             self.position,
                                             self.state, self.token, None)
            return ParseResultType.ERROR

        action = self.state.actions.get(self.token.symbol.index, None)
        if action is None:
            # Syntax error_info by an unexpected symbol
            expected_symbols = []
            for action in self.state.actions.itervalues():
                if action.symbol.type in (SymbolType.TERMINAL,
                                          SymbolType.END_OF_FILE,
                                          SymbolType.GROUP_START,
                                          SymbolType.GROUP_END):
                    expected_symbols.append(action.symbol)
            self.error_info = ParseErrorInfo(ParseErrorType.SYNTAX_ERROR,
                                             self.position,
                                             self.state, self.token,
                                             expected_symbols)
            return ParseResultType.ERROR

        if   action.type == LALRActionType.SHIFT:
            # Shift
            self.state = action.target
            item = ParseItem(self.state, token=self.token)
            self.stack.append(item)
            self.token_used = True
            return ParseResultType.SHIFT

        elif action.type == LALRActionType.REDUCE:
            # Reduce/Production
            production = action.target
            handles = []
            trimmed = (self.trim_reduction and
                       len(production.handles) == 1 and
                       production.handles[0].type == SymbolType.NON_TERMINAL)
            if trimmed:
                top_state = self.stack[-2].state
            else:
                for i in xrange(len(production.handles)):
                    handles.insert(0, self.stack.pop(-1))
                top_state = self.stack[-1].state

            # Reduce/Goto
            goto_action = top_state.actions[production.head.index]
            if goto_action.type != LALRActionType.GOTO:
                self.error_info = ParseErrorInfo(ParseErrorType.INTERNAL_ERROR,
                                                 self.position,
                                                 self.state, self.token, None)
                return ParseResult.ERROR
            self.state = goto_action.target
            if trimmed:
                item = self.stack[-1]
                item.state = self.state
                item.production = production
                return ParseResultType.REDUCE_ELIMINATED
            else:
                item = ParseItem(self.state, production=production)
                self.stack.append(item)
                item.handles = handles
                self.reduction = Reduction(production, item, handles)
                return ParseResultType.REDUCE

        elif action.type == LALRActionType.GOTO:
            # Goto
            self.error_info = ParseErrorInfo(ParseErrorType.INTERNAL_ERROR,
                                             self.position,
                                             self.state, self.token, None)
            return ParseResultType.ERROR

        elif action.type == LALRActionType.ACCEPT:
            # Accept
            self.result = self.stack[-1]
            return ParseResultType.ACCEPT

        else:
            # Internal Error
            self.error_info = ParseErrorInfo(ParseErrorType.INTERNAL_ERROR,
                                             self.position,
                                             self.state, self.token, None)
            return ParseResultType.ERROR

    def parse_reduce(self):
        """ Perform multiple parse-steps until accept or reduce or error.
        """
        while True:
            ret = self.parse_step()
            if ret in (ParseResultType.ACCEPT,
                       ParseResultType.REDUCE,
                       ParseResultType.ERROR):
                return ret

    def parse_all(self, handler=None):
        """ Perform all parse-steps until accept or error.
            In any parsing steps, handler will be invoked with a parsing state.
        """
        if handler:
            while True:
                ret = self.parse_step()
                if   ret == ParseResultType.ACCEPT:
                    handler(ret, self.top)
                    return ret
                elif ret == ParseResultType.SHIFT:
                    handler(ret, self.top)
                elif ret == ParseResultType.REDUCE:
                    handler(ret, self.reduction)
                elif ret == ParseResultType.REDUCE_ELIMINATED:
                    handler(ret, self.top)
                elif ret == ParseResultType.ERROR:
                    handler(ret, self.error_info)
                    return ret
        else:
            while True:
                ret = self.parse_step()
                if ret in (ParseResultType.ACCEPT,
                           ParseResultType.ERROR):
                    return ret
