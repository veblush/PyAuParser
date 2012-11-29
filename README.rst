===================================================
PyAuParser - GOLD Parser Engine for Python
===================================================

:Version: 0.5
:Author: Esun Kim (veblush+git_at_gmail_com)
:Download: http://pypi.python.org/pypi/pyauparser
:Source: https://github.com/veblush/pyauparser
:Keywords: python, goldparser, parser, lalr

.. contents::
    :local:

Overview
========

New python engine for GOLD Parser. It supports unicode and new .egt file format.

Installation
============

You can install arrow from pip::

	$ pip install pyauparser

Tutorial
========

Prepare a Grammar
-----------------

First we need a grammar of language for parsing. Pyauparser use a .egt file which is
compiled from .grm file which consists of text-formatted grammar definitions.

You can write a .grm file with GOLD Parser or alternatives with GOLD-Meta-Language_.
And instead of writing you can find lots of grammar files of popular languages at Grammars_.

.. _GOLD-Meta-Language: http://goldparser.org/doc/grammars/index.htm
.. _Grammars: http://goldparser.org/grammars/index.htm

Let's start with a simple calculator grammar. It consists of number, +, -, ``*``, /, unary -, parenthesis. ::

	"Start Symbol" = <E>

	{Digi9} = {Digit} - ['0']
	Num     = '0' | {Digi9}{Digit}*

	<E>   ::= <E> '+' <M> 
	       |  <E> '-' <M> 
	       |  <M> 
	
	<M>   ::= <M> '*' <N> 
	       |  <M> '/' <N> 
	       |  <N> 
	
	<N>   ::= '-' <V> 
	       |  <V> 
	
	<V>   ::= Num
	       |  '(' <E> ')'

Compile a .grm file with GOLD Parser and save table data to a .egt file.
We need only .egt file for a further parsing process. (from now .grm file is not necessary.)

Import Library
--------------

Simply import::

	import pyauparser

Load a Grammar
--------------

After preparing a .egt gramma file, we can load a grammar file now.
Load a grammar as following::

	g = pyauparser.Grammar.load_file("data/operator.egt")

Pyauparser doesn't support old .cgt file format.
But if you have a .grm file, you can make a .egt file with GOLD Parser 5 or newer.

Parse
-----

With grammar, you can parse a string or a file. There are two way to handle parsing results.
First one is an event-driven way as following::

	def callback(ret, arg):
            print "{0}\t{1}".format(get_enum_name(pyauparser.parser.ParseResultType, ret), arg)
	pyauparser.parse_string(g, "-2*(3+4)-5", handler=callback)

Result is following::

	SHIFT   S=1, V=- u'-'
	SHIFT   S=3, V=Num u'2'
	REDUCE  P=8, H=(S=8, V=<V> ::= Num), Hs=[(S=3, V=Num u'2')]
	REDUCE  P=6, H=(S=6, V=<N> ::= - <V>), Hs=[(S=1, V=- u'-'), (S=8, V=<V> ::= Num)]
	REDUCE  P=5, H=(S=5, V=<M> ::= <N>), Hs=[(S=6, V=<N> ::= - <V>)]
	...

It may look complicated but will be handled in a simple way.
Second one is a creating whole parse tree way as following::

	tree = pyauparser.parse_string_to_tree(g, "-2*(3+4)-5")

Parser create a parse tree from string and return it.
You can traverse a tree in a way you want and evaluate it freely.
Tree can be dumped using dump() method of tree::

	tree.dump()

Result is following::

	<E> ::= <E> - <M>
	  <E> ::= <M>
	    <M> ::= <M> * <N>
	      <M> ::= <N>
	       <N> ::= - <V>
	         - '-'
	          <V> ::= Num
	            Num '2'
	      * '*'
	      <N> ::= <V>
	...

Link: https://github.com/veblush/PyAuParser/blob/master/sample/tutorial1.py

Evaluate with parsing events
----------------------------

Because LALR is a bottom-up parser, every parsing event occurs in a bottom up way.
And if there is a way to evaluate a parsed string from bottom-up, we can use an event-driven
eveluation process as following::

	# construct event-handler. 
	# dict(ProductionRule to evaluation handler)
	# every handler get child handles and return a calculated value of node.
	h = pyauparser.ProductionHandler({
	    '<E> ::= <E> + <M>': lambda c: c[0] + c[2],
	    '<E> ::= <E> - <M>': lambda c: c[0] - c[2],
	    '<E> ::= <M>':       lambda c: c[0],
	    '<M> ::= <M> * <N>': lambda c: c[0] * c[2],
	    '<M> ::= <M> / <N>': lambda c: c[0] / c[2],
	    '<M> ::= <N>':       lambda c: c[0],
	    '<N> ::= - <V>':     lambda c: -c[1],
	    '<N> ::= <V>':       lambda c: c[0],
	    '<V> ::= Num':       lambda c: int(c[0].lexeme),
	    '<V> ::= ( <E> )':   lambda c: c[1],
	}, g)

	# parse string with handler
	pyauparser.parse_string(g, "-2*(3+4)-5", handler=h)
	print "Result = {0}".format(h.result)

Result is following::

	Result = -19

Link: https://github.com/veblush/PyAuParser/blob/master/sample/tutorial2.py

Evaluate with a syntax tree
---------------------------

Sometimes we need a whole parse tree. Because it is easy to traverse and manipulate.
If you need a value of sibling nodes or parents while evaluating a tree, this is what you're finding::

	# create tree first
	tree = pyauparser.parse_string_to_tree(g, "-2*(3+4)-5")

	# evaluate a parse tree by traverse nodes
	def evaluate(node):
	    r = lambda s: g.get_production(s).index
	    h = {
	        r('<E> ::= <E> + <M>'): lambda c: e(c[0]) + e(c[2]),
	        r('<E> ::= <E> - <M>'): lambda c: e(c[0]) - e(c[2]),
	        r('<E> ::= <M>'):       lambda c: e(c[0]),
	        r('<M> ::= <M> * <N>'): lambda c: e(c[0]) * e(c[2]),
	        r('<M> ::= <M> / <N>'): lambda c: e(c[0]) / e(c[2]),
	        r('<M> ::= <N>'):       lambda c: e(c[0]),
	        r('<N> ::= - <V>'):     lambda c: -e(c[1]),
	        r('<N> ::= <V>'):       lambda c: e(c[0]),
	        r('<V> ::= Num'):       lambda c: int(c[0].lexeme),
	        r('<V> ::= ( <E> )'):   lambda c: e(c[1]),
	    }
	    def e(node):
	        handler = h[node.production.index]
	        return handler(node.childs)
	    return e(node)

	result = evaluate(tree)
	print "Result = {0}".format(result)

Result is following::

	Result = -19

Link: https://github.com/veblush/PyAuParser/blob/master/sample/tutorial3.py

Simplified Tree
---------------

A parse tree is quite verbose to capture structure correctly. Therefore it's necessary to abstract a tree.
Usually there is an additional process to transform a parse tree to an abstract syntax tree. It's however bothersome.
To handle this problem, a feature building a simplified tree is provided. Simply call the following function::

	g.get_production('<V> ::= ( <E> )').sr_forward_child = True
	tree = pyauparser.parse_string_to_stree(g, "-2*(1+2+4)-2-2-1")
	tree.dump()

Result is following::

	<E> ::= <E> - <M>
	  <M> ::= <M> * <N>
	    <N> ::= - <V>
	      Num '2'
	    <E> ::= <E> + <M>
	      Num '1'
	      Num '2'
	      Num '4'
	  Num '2'
	  Num '2'
	  Num '1'

You can see that a result tree is very essential. The way evaluates a tree is following::

	def evaluate(node):
	    r = lambda s: g.get_production(s).index
	    h = {
	        r('<E> ::= <E> + <M>'): lambda c: reduce(lambda x, y: x + y, (e(d) for d in c)),
	        r('<E> ::= <E> - <M>'): lambda c: reduce(lambda x, y: x - y, (e(d) for d in c)),
	        r('<M> ::= <M> * <N>'): lambda c: reduce(lambda x, y: x * y, (e(d) for d in c)),
	        r('<M> ::= <M> / <N>'): lambda c: reduce(lambda x, y: x / y, (e(d) for d in c)),
	        r('<N> ::= - <V>'):     lambda c: -e(c[0]),
	    }
	    def e(node):
	        if node.token:
	                return int(node.token.lexeme)
	    else:
	                handler = h.get(node.production.index, None)
	                return handler(node.childs) if handler else e(node.childs[0])
	    return e(node)
	
	result = evaluate(tree)
	print "Result = {0}".format(result)

Result is following::

	Result = -19

Link: https://github.com/veblush/PyAuParser/blob/master/sample/tutorial4.py

Embedding a Grammar
-------------------

Basically we use a .egt grammar file exported from GOLD parser. Because of that
we can dynamically use any grammar file on running but sometimes embedding grammar files is
cumbersome or impossible. To handle this problem a static python module consists of
grammar information can be generated as following::

	auparser class data/operator.egt grammar_operator.py

We got grammar_operator.py. By import a grammar module and call load function grammar 
instance is created without an .egt file as following::

	import grammar_operator
	g = grammar_operator.load()

Link: https://github.com/veblush/PyAuParser/blob/master/sample/tutorial5.py

Changelog
=========

* 0.5

  * First release
