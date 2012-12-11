#!/usr/bin/python2

import os
import sys
import pyauparser
from pyauparser.parser import LALRActionType
import csv


def get_charset_desc(cs):
    chrs = sum(r[1] - r[0] + 1 for r in cs.ranges)

    if chrs <= 10:
        s = ""
        for r in cs.ranges:
            for o in range(r[0], r[1] + 1):
                c = chr(o)
                if   c == '"':
                    s += '\\" '
                elif c == '\\':
                    s += '\\\\ '
                elif o >= 33:
                    s += c + " "
                else:
                    s += "#{0} ".format(o)
    else:
        s = ""
        for r in cs.ranges:
            if r[1] - r[0] == 0:
                s += "#{0} ".format(r[0])
            else:
                s += "#{0}~#{1} ".format(r[0], r[1])

    return s.strip(" ")


def dfa_to_dot(g, dot_path, output_dot_path, output_png_path):
    of = open(output_dot_path, "wt")
    of.write("digraph G {\n")
    of.write("ranksep=0.1\n")
    of.write("nodesep=0.1\n")
    of.write('ratio="compress"\n')

    # init node
    of.write('s [ label="" shape="plaintext" ]\n'.format())

    # nodes
    for s in g.dfastates.itervalues():
        if s.accept_symbol:
            of.write('n{0} [ label="{1}" shape="doublecircle" ]\n'.format(
                s.index, s.accept_symbol.name))
        else:
            of.write('n{0} [ label="" shape="circle" ]\n'.format(
                s.index))

    # transition
    of.write('s -> n{0} [ label=" start"]\n'.format(g.dfainit.index))
    for s in g.dfastates.itervalues():
        for e in s.edges:
            of.write('n{0} -> n{1} [ label=" {2}" ]\n'.format(
                s.index, e.target.index, get_charset_desc(e.charset)))

    of.write("}\n")
    of.close()

    if output_png_path:
        import subprocess
        subprocess.call([dot_path, "-Tpng", "-o",
                         output_png_path, output_dot_path])


def lalr_to_csv(g, csv_path):
    writer = csv.writer(open(csv_path, 'wb'), dialect='excel')
    writer.writerow([""] + [s.id for s in g.symbols.itervalues()])
    for s in g.lalrstates.itervalues():
        row = ["{0}".format(s.index)]
        for sym in xrange(len(g.symbols)):
            if sym in s.actions:
                a = s.actions[sym]
                if a.type == LALRActionType.SHIFT:
                    row.append("S")
                elif a.type == LALRActionType.REDUCE:
                    row.append("R:{0}".format(a.target.index))
                elif a.type == LALRActionType.GOTO:
                    row.append("G:{0}".format(a.target.index))
                elif a.type == LALRActionType.ACCEPT:
                    row.append("A")
            else:
                row.append("")

        writer.writerow(row)


def main():
    g = pyauparser.Grammar.load_file("data/operator.egt")
    dfa_to_dot(g,
               "dot.exe",
               "data/temp_operator_dfa.dot",
               "data/temp_operator_dfa.png")
    lalr_to_csv(g, "data/temp_operator_lalr.csv")
    print "done"


if __name__ == "__main__":
    main()
