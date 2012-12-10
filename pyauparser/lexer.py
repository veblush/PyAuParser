import os
import sys
import grammar


class Token(object):
    """Token which is a result from Lexer
       symbol: symbol in grammar
       lexeme: text hit
    """

    def __init__(self, symbol, lexeme, position):
        self.symbol = symbol
        self.lexeme = lexeme
        self.position = position

    def __str__(self):
        return "{0} {1}".format(self.symbol.id, repr(self.lexeme))


class Lexer(object):
    """Lexical Analyzer class which generate tokens from string.
       It works by a DFA in grammar.
    """

    def __init__(self, grammar):
        self.grammar = grammar
        self._load(None, False)

    def load_file(self, file_or_path, encoding=None):
        """ Load a file to lexer.
            File_or_path could be file object or file name.
        """
        if (isinstance(file_or_path, str) or
            isinstance(file_or_path, unicode)):
            import codecs
            if encoding:
                self._load(codecs.open(file_or_path, encoding=encoding), True)
            else:
                self._load(open(file_or_path, "rb"), False)
        else:
            self._load(file_or_path, encoding is not None)

    def load_string(self, s):
        """ Load a string to lexer.
        """
        import StringIO
        self._load(StringIO.StringIO(s), s is unicode)

    def _load(self, file, is_unicode):
        self.file = file
        self.is_unicode = is_unicode
        self.buf = u"" if is_unicode else str()
        self.buf_cur = 0
        self.buf_remain = 0
        self.line = 1
        self.column = 1
        self.group_stack = []

    def _load_buffer(self):
        # shrink buffer
        if self.buf_cur >= 4096:
            self.buf = self.buf[self.buf_cur:]
            self.buf_cur = 0
        # read into buffer
        self.buf += self.file.read(4096)
        self.buf_remain = len(self.buf) - self.buf_cur

    def _consume_buffer(self, n):
        # update line, column position
        start = self.buf_cur
        new_line_i = -1
        while True:
            i = self.buf.find("\n", start, self.buf_cur + n)
            if i != -1:
                start = new_line_i = i + 1
                self.line += 1
            else:
                if new_line_i == -1:
                    self.column += n
                else:
                    self.column = 1 + self.buf_cur + n - new_line_i
                break
        # manipulate buffer
        if n < self.buf_remain:
            self.buf_cur += n
            self.buf_remain -= n
        else:
            self.buf = u"" if self.is_unicode else str()
            self.buf_cur = 0
            self.buf_remain = 0

    @property
    def position(self):
        return (self.line, self.column)

    def peek_token(self):
        """ peek next token and return it
            it doens't change any cursor state of lexer.
        """
        state = self.grammar.dfainit
        cur = 0
        hit_symbol = None
        while True:
            if cur < self.buf_remain:           # peek 1 char
                c = self.buf[self.buf_cur + cur]
            else:
                self._load_buffer()
                if cur < self.buf_remain:
                    c = self.buf[self.buf_cur + cur]
                else:
                    break                       # if EOF
            cur += 1

            next_index = -1                     # find next state
            c_ord = ord(c)
            for (r_min, r_max), target_index, target in state.edges_lookup:
                if c_ord >= r_min and c_ord <= r_max:
                    next_index = target_index
                    next_state = target
                    break

            if   next_index == -3:
                continue
            elif next_index == -2:
                hit_cur = cur
                continue
            elif next_index == -1:
                break
            else:
                state = next_state
                if next_state.accept_symbol:    # keep acceptable
                    hit_symbol = next_state.accept_symbol
                    hit_cur = cur

        if hit_symbol:
            lexeme = self.buf[self.buf_cur:self.buf_cur + hit_cur]
            return Token(hit_symbol, lexeme, self.position)
        else:
            if cur == 0:
                return Token(self.grammar.symbol_EOF, "", self.position)
            else:
                lexeme = self.buf[self.buf_cur:self.buf_cur + cur]
                return Token(self.grammar.symbol_Error, lexeme, self.position)

    def read_token(self):
        """ Read next token and return it.
            It moves a read cursor forward and it processes a lexical group.
        """
        while True:
            token = self.peek_token()

            # check if a start of new group
            if token.symbol.type == grammar.SymbolType.GROUP_START:
                symbol_group = [g for g in self.grammar.symbolgroups.itervalues() if g.start == token.symbol][0]
                if len(self.group_stack) == 0:
                    nest_group = True
                else:
                    nest_group = symbol_group in self.group_stack[-1][0].nesting_groups
            else:
                nest_group = False

            if nest_group:
                # into nested
                self._consume_buffer(len(token.lexeme))
                self.group_stack.append([symbol_group,
                                         token.lexeme, token.position])

            elif len(self.group_stack) == 0:
                # token in plain
                self._consume_buffer(len(token.lexeme))
                return token

            elif self.group_stack[-1][0].end == token.symbol:
                # out of nested
                pop = self.group_stack.pop()
                if pop[0].ending_mode == grammar.EndingModeType.CLOSED:
                    pop[1] = pop[1] + token.lexeme
                    self._consume_buffer(len(token.lexeme))
                if len(self.group_stack) == 0:
                    return Token(pop[0].container, pop[1], pop[2])
                else:
                    self.group_stack[-1][1] = self.group_stack[-1][1] + pop[1]

            elif token.symbol == self.grammar.symbol_EOF:
                # EOF in nested
                return token

            else:
                # token in nested
                top = self.group_stack[-1]
                if top[0].advance_mode == grammar.AdvanceModeType.TOKEN:
                    top[1] = top[1] + token.lexeme
                    self._consume_buffer(len(token.lexeme))
                else:
                    top[1] = top[1] + token.lexeme[0]
                    self._consume_buffer(1)

    def read_token_all(self):
        """ Read all token until EOF.
            If no error return END_OF_FILE, otherwise ERROR.
        """
        ret = []
        while True:
            token = self.read_token()
            ret.append(token)
            if token.symbol.type in (grammar.SymbolType.END_OF_FILE,
                                     grammar.SymbolType.ERROR):
                break
        return ret
