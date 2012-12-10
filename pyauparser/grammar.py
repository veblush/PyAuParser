import os
import sys


# get a name of enumeration from a value of it
def get_enum_name(cls, value):
    return [k for k, v in cls.__dict__.iteritems() if v == value][0]


class Property(object):
    """Property entity of grammar
       http://goldparser.org/doc/egt/record-property.htm
    """

    def __init__(self, index, name, value):
        self.index = index
        self.name = name
        self.value = value

    def __repr__(self):
        return u"Property({0})".format(u", ".join((
            repr(self.index), repr(self.name), repr(self.value))))

    def __str__(self):
        return "{0}:{1}={2}".format(
            self.index, self.name, self.value.encode("ascii", "replace"))


class CharacterSet(object):
    """Character set information used for DFA in lexical analysis
       http://goldparser.org/doc/egt/record-char-set.htm
    """

    def __init__(self, index, uniplane, ranges):
        self.index = index
        self.uniplane = uniplane
        self.ranges = ranges

    def __repr__(self):
        return u"CharacterSet({0})".format(u", ".join((
            repr(self.index), repr(self.uniplane), repr(self.ranges))))

    def __str__(self):
        return "{0}:P={1} R={2}".format(
            self.index, self.uniplane, self.ranges)


class Symbol(object):
    """Symbol entity including terminals, nonterminals.
       http://goldparser.org/doc/egt/record-symbol.htm
    """

    def __init__(self, index, name, type):
        self.index = index
        self.name = name
        self.type = type

    @property
    def id(self):
        if self.type == SymbolType.NON_TERMINAL:
            return u"<{0}>".format(self.name)
        elif self.type == SymbolType.TERMINAL:
            return self.name
        else:
            return u"({0})".format(self.name)

    def __repr__(self):
        return u"Symbol({0})".format(u", ".join((
            repr(self.index), repr(self.name), repr(self.type))))

    def __str__(self):
        return "{0} ({1})".format(self.name,
                                  get_enum_name(SymbolType, self.type))


class SymbolType:
    NON_TERMINAL = 0
    TERMINAL = 1
    NOISE = 2
    END_OF_FILE = 3
    GROUP_START = 4
    GROUP_END = 5
    DECREMENTED = 6
    ERROR = 7


class SymbolGroup(object):
    """Group information used for a nested structure like comment, etc.
       http://goldparser.org/doc/egt/record-group.htm
    """

    def __init__(self, index, name, container, start, end,
                 advance_mode, ending_mode, nesting_groups):
        self.index = index
        self.name = name
        self.container = container
        self.start = start
        self.end = end
        self.advance_mode = advance_mode
        self.ending_mode = ending_mode
        self.nesting_groups = nesting_groups

    def __repr__(self):
        return u"Symbol({0})".format(u", ".join((
            repr(self.index), repr(self.name), repr(self.container.index),
            repr(self.start.index), repr(self.end.index),
            repr(self.advance_mode), repr(self.ending_mode),
            repr([group.index for group in self.nesting_groups]))))

    def __str__(self):
        return "{0}:{1}={2} {3} {4} {5} {6} {7}".format(
            self.index, self.name,
            self.container.id,
            self.start.id,
            self.end.id,
            get_enum_name(AdvanceModeType, self.advance_mode),
            get_enum_name(EndingModeType, self.ending_mode),
            [group.index for group in self.nesting_groups])


class AdvanceModeType:
    TOKEN = 0
    CHARACTER = 1


class EndingModeType:
    OPEN = 0
    CLOSED = 1


class Production(object):
    """Production Rule information
       http://goldparser.org/doc/egt/record-production.htm
    """

    def __init__(self, index, head, handles):
        self.index = index
        self.head = head
        self.handles = handles

    @property
    def id(self):
        return "{0} ::= {1}".format(
            self.head.id, " ".join(h.id for h in self.handles))

    def __repr__(self):
        return u"Production({0})".format(u", ".join((
            repr(self.index), repr(self.head.index),
            repr([h.index for h in self.handles]))))

    def __str__(self):
        return self.id


class DFAState(object):
    """DFA State for a lexical analysis
       http://goldparser.org/doc/egt/record-dfa-state.htm
    """

    def __init__(self, index, accept_symbol, edges):
        self.index = index
        self.accept_symbol = accept_symbol
        self.edges = edges

    def __repr__(self):
        return u"DFAState({0})".format(u", ".join((
            repr(self.index),
            repr(self.accept_symbol.index) if self.accept_symbol else "None",
            repr(self.edges))))

    def __str__(self):
        return "{0}: Accept({1}) Edges({2})".format(
            self.index,
            self.accept_symbol.id if self.accept_symbol else "",
            "; ".join((str(edge) for edge in self.edges)))


class DFAEdge(object):
    """DFA edge between states.
    """

    def __init__(self, charset, target):
        self.charset = charset
        self.target = target

    def __repr__(self):
        return u"DFAEdge({0})".format(u", ".join((
            repr(self.charset.index), repr(self.target.index))))

    def __str__(self):
        return "{0} -> {1}".format(
            self.charset.index, self.target.index)


class LALRState(object):
    """LALR State used for LALR parsing.
       http://goldparser.org/doc/egt/record-lalr-state.htm
    """

    def __init__(self, index, actions):
        self.index = index
        self.actions = actions

    def __repr__(self):
        return u"LALRState({0})".format(u", ".join((
            repr(self.index),
            "{" + ", ".join("{0}:{1}".format(repr(k), repr(v)) for k, v in sorted(self.actions.iteritems())) + "}")))

    def __str__(self):
        return "{0}: {1}".format(
            self.index,
            "; ".join((str(a) for k, a in sorted(self.actions.iteritems()))))


class LALRAction(object):
    """LALR Action entity for LALR parsing.
    """

    def __init__(self, symbol, type, target):
        self.symbol = symbol
        self.type = type
        self.target = target

    def __repr__(self):
        return u"LALRAction({0})".format(u", ".join((
            repr(self.symbol.index) if self.symbol else "None",
            repr(self.type),
            repr(self.target.index) if self.target else "None")))

    def __str__(self):
        return "{0} -> {1} : {2}".format(
            self.symbol.id if self.symbol else "",
            get_enum_name(LALRActionType, self.type),
            self.target.index if self.target else "")


class LALRActionType:
    SHIFT = 1
    REDUCE = 2
    GOTO = 3
    ACCEPT = 4


class Grammar(object):
    """Grammar.
       It holds a specific grammar table created by GOLD Parser and
       provides  information to lexer and parser.
    """

    def __init__(self):
        self.properties = {}
        self.charsets = {}
        self.symbols = {}
        self.symbolgroups = {}
        self.productions = {}
        self.dfainit = 0
        self.dfastates = {}
        self.lalrinit = 0
        self.lalrstates = {}
        self.symbol_EOF = None
        self.symbol_Error = None
        self.symbol_id_lookup = {}
        self.production_id_lookup = {}

    @staticmethod
    def load_file(file_or_path):
        """Load grammar information from file.
           http://goldparser.org/doc/egt/index.htm
        """
        if (isinstance(file_or_path, str) or
            isinstance(file_or_path, unicode)):
            with open(file_or_path, "rb") as file:
                return Grammar._load(file)
        else:
            return Grammar._load(file_or_path)

    @staticmethod
    def _load(f):
        # deserialize helper functions
        def read_empty():
            return None

        def read_byte():
            c = f.read(1)
            return c[0] if len(c) == 1 else None

        def read_bool():
            c = f.read(1)
            return ord(c[0]) == 1 if len(c) == 1 else None

        def read_short():
            c = f.read(2)
            return ord(c[0]) + ord(c[1]) * 256 if len(c) == 2 else None

        def read_string():
            s = ""
            while True:
                c = f.read(2)
                if len(c) < 2 or (ord(c[0]) == 0 and ord(c[1]) == 0):
                    break
                s += c
            return s.decode("utf-16le")

        def read_value():
            t = f.read(1)
            if   t == 'E':
                return read_empty()
            elif t == 'b':
                return read_byte()
            elif t == 'B':
                return read_bool()
            elif t == 'I':
                return read_short()
            elif t == 'S':
                return read_string()
            else:
                return None

        # start
        grm = Grammar()
        header = read_string()
        if header != u"GOLD Parser Tables/v5.0":
            raise Exception("Unknown Header: " + header)

        # read records
        while read_byte() == 'M':
            v = []
            for x in range(read_short()):
                v.append(read_value())
            t = v[0] if len(v) > 0 else None
            if   t == 'p':  # Property
                grm.properties[v[1]] = Property(v[1], v[2], v[3])
            elif t == 't':  # Table Counts
                tablecounts = tuple(v[1:])
            elif t == 'c':  # Character Set Table
                grm.charsets[v[1]] = CharacterSet(
                    v[1], v[2],
                    tuple([(v[i * 2 + 5], v[i * 2 + 6]) for i in range(v[3])]))
            elif t == 'S':  # Symbol Record
                grm.symbols[v[1]] = Symbol(v[1], v[2], v[3])
            elif t == 'g':  # Group Record
                grm.symbolgroups[v[1]] = SymbolGroup(
                    v[1], v[2], v[3], v[4], v[5], v[6], v[7], tuple(v[10:]))
            elif t == 'R':  # Production Record
                grm.productions[v[1]] = Production(v[1], v[2], tuple(v[4:]))
            elif t == 'I':  # Initial States Record
                grm.dfainit, grm.lalrinit = v[1:]
            elif t == 'D':  # DFA State Record
                grm.dfastates[v[1]] = DFAState(
                    v[1],
                    v[3] if v[2] else None,
                    tuple([DFAEdge(v[i * 3 + 5], v[i * 3 + 6])
                           for i in range((len(v) - 5) / 3)]))
            elif t == 'L':  # LALR State Record
                grm.lalrstates[v[1]] = LALRState(
                    v[1],
                    dict([(v[i * 4 + 3],
                           LALRAction(v[i * 4 + 3],
                                      v[i * 4 + 4],
                                      v[i * 4 + 5]))
                          for i in range((len(v) - 3) / 4)]))
            else:
                raise Exception("Unknown type: " + t)

        # check read counts
        readcounts = (len(grm.symbols),
                      len(grm.charsets),
                      len(grm.productions),
                      len(grm.dfastates),
                      len(grm.lalrstates),
                      len(grm.symbolgroups))
        if tablecounts != readcounts:
            raise Exception("Table Count Mismatch!")

        grm._process_after_load()
        return grm

    def _process_after_load(self):
        self._link_reference()
        self._build_dfa_lookup()
        self._set_single_lexeme_symbol()
        self._set_simplication_rule()

    def _link_reference(self):
        # To optimize lookup table process in lex and parse operations,
        # change index to references.

        for g in self.symbolgroups.itervalues():
            g.container = self.symbols[g.container]
            g.start = self.symbols[g.start]
            g.end = self.symbols[g.end]
            g.nesting_groups = tuple((self.symbolgroups[i] for i in g.nesting_groups))

        for p in self.productions.itervalues():
            p.head = self.symbols[p.head]
            p.handles = tuple((self.symbols[h] for h in p.handles))

        self.dfainit = self.dfastates[self.dfainit]

        for s in self.dfastates.itervalues():
            s.accept_symbol = self.symbols[s.accept_symbol] if s.accept_symbol else None
            s.edges = tuple((DFAEdge(self.charsets[e.charset], self.dfastates[e.target]) for e in s.edges))

        self.lalrinit = self.lalrstates[self.lalrinit]

        for s in self.lalrstates.itervalues():
            for a in s.actions.itervalues():
                a.symbol = self.symbols[a.symbol]
                if   a.type == LALRActionType.SHIFT:
                    a.target = self.lalrstates[a.target]
                elif a.type == LALRActionType.REDUCE:
                    a.target = self.productions[a.target]
                elif a.type == LALRActionType.GOTO:
                    a.target = self.lalrstates[a.target]

        self.symbol_EOF = [s for s in self.symbols.itervalues() if s.type == SymbolType.END_OF_FILE][0]
        self.symbol_Error = [s for s in self.symbols.itervalues() if s.type == SymbolType.ERROR][0]

        for s in self.symbols.itervalues():
            self.symbol_id_lookup[s.id] = s

        for p in self.productions.itervalues():
            self.production_id_lookup[p.id] = p

    def _build_dfa_lookup(self):
        # make a merged lookup-table for fast finding next state
        for s in self.dfastates.itervalues():
            edges_list = []
            for e in s.edges:
                target_index = e.target.index
                if s.index == target_index:
                    target_index = -2 if s.accept_symbol else -3
                u = e.charset.uniplane * 0x10000
                edges_list.extend(
                    ((u + r[0], u + r[1]), target_index, e.target) for r in e.charset.ranges)
            s.edges_lookup = tuple(sorted(edges_list, key=lambda x: x[0][0]))

    def _set_single_lexeme_symbol(self):
        # find terminals having only single lexeme.
        # (by finding dfa-state nodes has one-acyclic path from an initial state)
        for s in self.dfastates.itervalues():
            s.path_count = None
        self.dfainit.path_count = 1
        left_nodes = [self.dfainit]
        while len(left_nodes) > 0:
            s = left_nodes.pop(0)
            for edge in s.edges:
                if edge.target.path_count == 1:
                    # multiple path found.
                    # all nodes from this have multiple paths
                    left_m_nodes = [edge.target]
                    while len(left_m_nodes) > 0:
                        m = left_m_nodes.pop(0)
                        m.path_count = 2
                        for edge in m.edges:
                            if edge.target.path_count != 2:
                                left_m_nodes.append(edge.target)
                elif edge.target.path_count is None:
                    # new node found. keep going on.
                    edge.target.path_count = 1
                    left_nodes.append(edge.target)
        symbol_path_count_map = {}
        for s in self.dfastates.itervalues():
            if s.path_count == 1 and s.accept_symbol:
                symbol_path_count_map.setdefault(s.accept_symbol.index, 0)
                symbol_path_count_map[s.accept_symbol.index] += 1
        for symbol in self.symbols.itervalues():
            if symbol_path_count_map.get(symbol.index, 0) == 1:
                symbol.single_lexeme = True
            else:
                symbol.single_lexeme = False

    def _set_simplication_rule(self):
        # mark production flags
        for p in self.productions.itervalues():
            ts = [h for h in p.handles if h.type == SymbolType.TERMINAL]
            nts = [h for h in p.handles if h.type == SymbolType.NON_TERMINAL]
            its = [t for t in ts if not t.single_lexeme]

            p.sr_forward_child = ((len(nts) == 1 and len(ts) == 0) or
                                  (len(nts) == 0 and len(its) == 1) or
                                  (len(nts) == 0 and len(ts) == 1))
            p.sr_merge_child = False
            p.sr_listify_recursion = any(p.head.index == n.index for n in nts)
            p.sr_remove_single_lexeme = ((len(nts) > 0 or len(its) > 0) and
                                         (len(ts) - len(its) > 0))

    def get_symbol(self, id):
        return self.symbol_id_lookup.get(id, None)

    def get_production(self, id):
        return self.production_id_lookup.get(id, None)

    def export_to_txt(self, f):
        """Export information to a text file.
        """

        def print_dict_values(name, container):
            f.write(u"* {0}\n".format(name))
            for v in container.itervalues():
                f.write(u"\t{0}\n".format(v))
            f.write(u"\n")

        print_dict_values("properties", self.properties)
        print_dict_values("charsets", self.charsets)
        print_dict_values("symbols", self.symbols)
        print_dict_values("symbolgroups", self.symbolgroups)
        print_dict_values("productions", self.productions)

        f.write(u"* initial states\n")
        f.write(u"\tdfainit = {0}\n".format(self.dfainit.index))
        f.write(u"\tlalrinit = {0}\n".format(self.lalrinit.index))
        f.write(u"\n")

        print_dict_values("dfastates", self.dfastates)
        print_dict_values("lalrstates", self.lalrstates)

    def export_to_py(self, f):
        """Export information to a python file.
           With an exported py, grammar can be constructed without a egt file.
        """

        def repr_dict(name, container):
            f.write(u"\tgrm.{0} = {{\n".format(name))
            for k, v in sorted(container.iteritems()):
                f.write(u"\t\t{0}:{1},\n".format(repr(k), repr(v)))
            f.write(u"\t}\n")

        f.write(u"from pyauparser import *\n")

        f.write(u"\n")
        f.write(u"def load():\n")
        f.write(u"\tgrm = Grammar()\n")

        repr_dict("properties", self.properties)
        repr_dict("charsets", self.charsets)
        repr_dict("symbols", self.symbols)
        repr_dict("symbolgroups", self.symbolgroups)
        repr_dict("productions", self.productions)

        f.write(u"\tgrm.dfainit = {0}\n".format(self.dfainit.index))
        repr_dict("dfastates", self.dfastates)
        f.write(u"\tgrm.lalrinit = {0}\n".format(self.lalrinit.index))
        repr_dict("lalrstates", self.lalrstates)

        f.write(u"\tgrm._process_after_load()\n")
        f.write(u"\treturn grm\n")
