import os
import sys
import lexer
import parser
from grammar import SymbolType


class TreeNode(object):
    """TreeNode used for representing a parse-tree and a simplified-tree.
    """

    def __init__(self, production=None, childs=None, token=None):
        self.production = production
        self.childs = childs
        self.token = token

    @property
    def is_terminal(self):
        return self.token is not None

    @property
    def is_non_terminal(self):
        return self.production is not None

    def dump(self, depth=0):
        if self.is_non_terminal:
            print u"{0}{1}".format("  " * depth, 
                                   self.production)
            for c in self.childs:
                c.dump(depth + 1)
        elif self.is_terminal:
            print u"{0}{1} '{2}'".format("  " * depth,
                                         self.token.symbol.name,
                                         self.token.lexeme)
        else:
            print u"{0} None".format("  " * depth)


class TreeBuilder(object):
    """TreeBuilder build a concrete syntax tree (parse-tree)
    """

    def __init__(self):
        self.result = None

    def __call__(self, ret, arg):
        if ret == parser.ParseResultType.SHIFT:
            # create a terminal node
            arg.data = TreeNode(token=arg.token)

        elif ret == parser.ParseResultType.REDUCE:
            # create a non-terminal node
            arg.head.data = TreeNode(production=arg.production,
                                     childs=[h.data for h in arg.handles])

        elif ret == parser.ParseResultType.ACCEPT:
            self.result = arg.data


class SimplifiedTreeBuilder(object):
    """SimplifiedTreeBuilder build a simplified tree like an abstract
       syntax tree through parsing.
       Productions in grammar have sr_* properties controlling a tree shape.
    """

    def __init__(self):
        self.result = None

    def __call__(self, ret, arg):
        if ret == parser.ParseResultType.REDUCE:
            p = arg.production

            # make all handles into a list of child candidate.
            ccs = [(h, h.data) for h in arg.handles]

            # remove every symbol which has only single lexeme.
            if p.sr_remove_single_lexeme:
                ccs = [(cc[0], cc[1]) for cc in ccs 
                                      if cc[0].production or
                                         not cc[0].token.symbol.single_lexeme]

            # make their nodes for each terminal
            for i, cc in enumerate(ccs):
                if cc[0].token:
                    ccs[i] = (cc[0], TreeNode(token=cc[0].token))

            # forward a child node and drop me
            if p.sr_forward_child and len(ccs) == 1:
                arg.head.data = ccs[0][1]
                return

            # change a recursive child node to a flat list
            if p.sr_listify_recursion:
                for i, cc in enumerate(ccs):
                    if cc[0].production and cc[0].production.head.index == p.head.index:
                        if cc[0].production.index == p.index and cc[1].is_non_terminal:
                            ccs = (ccs[:i] + 
                                   [(None, c) for c in cc[1].childs] +
                                   ccs[i+1:])
                        elif len(cc[0].handles) == 0:
                            del ccs[i]
                        break

            # get children of a child and drop a child
            if p.sr_merge_child:
                for i, cc in enumerate(ccs):
                    if cc[0].production:
                        if (cc[1].is_non_terminal and 
                            cc[0].production.index == cc[1].production.index):
                            ccs = (ccs[:i] + 
                                   [(None, c) for c in cc[1].childs] +
                                   ccs[i+1:])
                        break

            # create a non-terminal node
            arg.head.data = TreeNode(production=arg.production,
                                     childs=[cc[1] for cc in ccs])

        elif ret == parser.ParseResultType.ACCEPT:
            self.result = arg.data
