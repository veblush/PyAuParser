#!/usr/bin/python2

import os
import sys
import pyauparser


def export_to_dot(root, dot_path, output_dot_path, output_png_path):
    of = open(output_dot_path, "wt")
    of.write("digraph G {\n")
    #of.write('size="4 4"\n')
    of.write("rankdir=BT\n")
    of.write("ranksep=0.1\n")
    of.write("nodesep=0.1\n")
    of.write('ratio="compress"\n')
    of.write('node [ fontname="Arial" fontsize=14 ]\n')
    last_node_id = [0]
    terminals = []
    def recur(node):
        last_node_id[0] += 1
        id = last_node_id[0]
        if node.production:
            # non-terminal
            if hasattr(node, "id"):
                of.write('n{0} [ label="{1},{2}\\n#{3}" shape="plaintext" ]\n'.format(
                    id, node.production.head.name, node.production.index, node.id))
            else:
                of.write('n{0} [ label="{1},{2}" shape="plaintext" ]\n'.format(
                    id, node.production.head.name, node.production.index))
            for child in node.childs:
                node_id = recur(child)
                of.write('n{0} -> n{1} [ arrowhead="none" ]\n'.format(node_id, id))
        else:
            # terminal
            terminals.append(id)
            txt = node.token.lexeme.replace("\\", "\\\\").replace('"', '\\"')
            if node.token.symbol.name == str(node.token.lexeme):
                of.write('n{0} [ shape="box" label="{1}" fontname="consolas" fontsize=18 width=0 ]\n'.format(id, txt))
            else:
                of.write('n{0} [ shape="record" label="{1}\\n{2}" fontname="consolas" fontsize=12 width=0 ]\n'.format(id, node.token.symbol.name, txt))
        return id
    recur(root)
    of.write("{ rank = same; " + ";".join('"n{0}"'.format(i) for i in terminals) + "}\n")
    of.write("}\n")
    of.close()

    if output_png_path:
        import subprocess
        subprocess.call([dot_path, "-Tpng", "-o", output_png_path, output_dot_path])


def main():
    g = pyauparser.Grammar.load_file("data/operator.egt")

    p = pyauparser.Parser(g)
    #p.trim_reduction = True
    p.load_file("Data/operator_sample_1.txt")

    builder = pyauparser.TreeBuilder()
    #g.get_production('<V> ::= ( <E> )').sr_forward_child = True
    #builder = pyauparser.SimplifiedTreeBuilder()

    # handler marking a creation order number on each node
    reduce_id = [0]
    def mark_id_handler(handler):
        def sub_handler(ret, arg):
            handler(ret, arg)
            if ret == pyauparser.ParseResultType.REDUCE:
                reduce_id[0] += 1
                arg.head.data.id = reduce_id[0]
        return sub_handler
    builder2 = mark_id_handler(builder)
    #builder2 = builder

    ret = p.parse_all(builder2)
    if ret != pyauparser.ParseResultType.ACCEPT:
        print p.error_info
        return

    result = builder.result
    result.dump()

    export_to_dot(result,
                  r"dot.exe",
                  r"Data/parse_tree.dot",
                  r"Data/parse_tree.png")
    print "done"


if __name__ == "__main__":
    main()
