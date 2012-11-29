import os
import sys
import getopt
import StringIO
import codecs
import pyauparser


def c_show(cmd_args):
    opts, args = getopt.getopt(cmd_args, "spP")

    mode = ""
    for o, a in opts:
        if o == "-s":
            mode = o
        elif o == "-p":
            mode = o
        elif o == "-P":
            mode = o

    egt_path = args[0]
    g = pyauparser.Grammar.load_file(egt_path)

    if mode == "":
        stio = StringIO.StringIO()
        g.export_to_txt(stio)
        print stio.getvalue().encode()
    elif mode == "-s":
        print "* symbols"
        for k, v in sorted(g.symbols.iteritems()):
            print('\t{0}\t{1}'.format(k, repr(v.pname)))
    elif mode == "-p":
        g = pyauparser.Grammar.load_file(egt_path)
        print "* productions"
        for k, v in sorted(g.productions.iteritems()):
            print('\t{0}\t{1}'.format(k, repr(v.pname)))
    elif mode == "-P":
        g = pyauparser.Grammar.load_file(egt_path)
        print "h = {"
        for k, v in sorted(g.productions.iteritems()):
            print('\t{0}: None,'.format(repr(v.pname)))
        print "}"


def c_class(cmd_args):
    opts, args = getopt.getopt(cmd_args, "e:")

    encoding = "utf-8"
    for o, a in opts:
        if o == "-e":
            encoding = a

    egt_path = args[0]
    g = pyauparser.Grammar.load_file(egt_path)

    py_path = cmd_args[1] if len(cmd_args) > 1 else None
    if py_path:
        f = codecs.open(py_path, "w", encoding)
        g.export_to_py(f)
        f.close()
        print("{0}: done".format(py_path))
    else:
        f = StringIO.StringIO()
        g.export_to_py(f)
        print(f.getvalue())


def c_lex(cmd_args):
    opts, args = getopt.getopt(cmd_args, "e:")

    encoding = None
    for o, a in opts:
        if o == "-e":
            encoding = a

    egt_path = args[0]
    data_path = args[1]

    g = pyauparser.Grammar.load_file(egt_path)
    lexer = pyauparser.Lexer(g)
    lexer.load_file(data_path, encoding=encoding)

    while True:
        position, token = lexer.position, lexer.read_token()
        print (token.symbol.name, token.lexeme, position)
        if   token.symbol.type == pyauparser.SymbolType.END_OF_FILE:
            break
        elif token.symbol.type == pyauparser.SymbolType.ERROR:
            print "ERROR:", token.lexeme
            return


def c_parse(cmd_args):
    opts, args = getopt.getopt(cmd_args, "e:t")

    encoding = None
    trim_reduction = False
    for o, a in opts:
        if o == "-e":
            encoding = a
        elif o == "-t":
            trim_reduction = True

    egt_path = args[0]
    data_path = args[1]

    g = pyauparser.Grammar.load_file(egt_path)
    p = pyauparser.Parser(g)
    p.load_file(data_path, encoding=encoding)
    p.trim_reduction = trim_reduction

    while True:
        ret = p.parse_step()
        if   ret == pyauparser.ParseResultType.ACCEPT:
            print "[Accept]"
            break
        elif ret == pyauparser.ParseResultType.SHIFT:
            token = p.token
            print "[Shift] {0} '{1}' ({2}:{3})".format(
                    token.symbol.name, token.lexeme, p.line, p.column)
        elif ret == pyauparser.ParseResultType.REDUCE:
            print "[Reduce] {0}".format(p.reduction.production)
        elif ret == pyauparser.ParseResultType.REDUCE_ELIMINATED:
            print "[ReduceEliminated]"
        elif ret == pyauparser.ParseResultType.ERROR:
            print "[Error] '{0}' ({1}:{2})".format(
                    p.error_info, p.line, p.column)
            return


def c_tree(cmd_args):
    opts, args = getopt.getopt(cmd_args, "e:s")

    encoding = None
    simplified = False
    for o, a in opts:
        if o == "-e":
            encoding = a
        elif o == "-s":
            simplified = True

    egt_path = args[0]
    data_path = args[1]

    g = pyauparser.Grammar.load_file(egt_path)
    try:
        if simplified:
            tree = pyauparser.parse_file_to_stree(g, data_path, encoding=encoding)
        else:
            tree = pyauparser.parse_file_to_tree(g, data_path, encoding=encoding)
        tree.dump()
    except pyauparser.ParseError as e:
        print(e)


def usage():
    print("auparser command ...")
    print "  h[elp]     : show help"
    print 
    print "  s[how]     : show information from a grammar file"
    print "    [options] egt"
    print "    -s show a symbol list"
    print "    -p show a production rule list"
    print "    -P show a production rule list as py dictionary"
    print
    print "  c[lass]    : create a module embedding a grammar file"
    print "    [options] egt [output]"
    print "    -e set output encoding"
    print
    print "  l[ex]      : show lexing procedure"
    print "    [options] egt data"
    print "    -e set input encoding"
    print
    print "  p[arse]    : show parsing procedure"
    print "    [options] egt data"
    print "    -e set input encoding"
    print "    -t use trim reduction"
    print
    print "  t[ree]     : print a tree built through parsing data"
    print "    [options] egt data"
    print "    -e set input encoding"
    print "    -s use a simplified tree builder"


def main():
    argv = sys.argv[1:]
    if len(argv) == 0:
        usage()
        sys.exit(2)

    cmd = argv[0].lower()
    cmd_args = argv[1:]
    if   cmd in ("h", "help"):
        c_usage()
    elif cmd in ("s", "show"):
        c_show(cmd_args)
    elif cmd in ("c", "class"):
        c_class(cmd_args)
    elif cmd in ("l", "lex"):
        c_lex(cmd_args)
    elif cmd in ("p", "parse"):
        c_parse(cmd_args)
    elif cmd in ("t", "tree"):
        c_tree(cmd_args)
    else:
        print "Unknown command. use help."
        sys.exit(2)

if __name__ == "__main__":
    main()
