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


def parse_and_write_dot_png(g, src_path, dot_path, png_path,
                            trim_reduction=False,
                            mark_id=False, simplified=False):
    p = pyauparser.Parser(g)
    p.trim_reduction = trim_reduction
    p.load_file(src_path)

    if simplified:
        builder = pyauparser.SimplifiedTreeBuilder()
    else:
        builder = pyauparser.TreeBuilder()

    if mark_id:
        reduce_id = [0]
        def mark_id_handler(handler):
            def sub_handler(ret, p):
                handler(ret, p)
                if ret == pyauparser.ParseResultType.REDUCE:
                    reduce_id[0] += 1
                    p.reduction.head.data.id = reduce_id[0]
            return sub_handler
        builder_p = mark_id_handler(builder)
    else:
        builder_p = builder

    ret = p.parse_all(builder_p)
    if ret != pyauparser.ParseResultType.ACCEPT:
        print p.error_info
        return

    print "* SRC:", src_path
    result = builder.result
    result.dump()
    export_to_dot(result, r"dot.exe", dot_path, png_path)
    print


def main():
    g = pyauparser.Grammar.load_file("data/operator.egt")

    src_path = r"data/operator_sample_1.txt"
    
    parse_and_write_dot_png(g, src_path, "data/temp_1.dot", "data/temp_1.png",
                            False, True, False)
    
    parse_and_write_dot_png(g, src_path, "data/temp_2.dot", "data/temp_2.png",
                            True, True, False)
    
    parse_and_write_dot_png(g, src_path, "data/temp_3.dot", "data/temp_3.png",
                            False, False, True)

    g.get_production('<V> ::= ( <E> )').sr_forward_child = True
    parse_and_write_dot_png(g, src_path, "data/temp_4.dot", "data/temp_4.png",
                            False, False, True)


if __name__ == "__main__":
    main()
