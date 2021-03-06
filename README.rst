===================================================
PyAuParser - GOLD Parser Engine for Python
===================================================

:Version: 0.53
:Author: Esun Kim (veblush+git_at_gmail_com)
:Download: http://pypi.python.org/pypi/PyAuParser
:Source: https://github.com/veblush/PyAuParser
:License: The MIT License `LICENSE`_
:Keywords: python, goldparser, parser, lalr

.. contents::
    :local:

.. _LICENSE: https://github.com/veblush/PyAuParser/blob/master/LICENSE.txt

Overview
========

New python engine for GOLD Parser. It supports unicode and new .egt file format.

Installation
============

You can install pyauparser from pip::

	$ pip install pyauparser

Tutorial
========

Prepare a Grammar
-----------------

First we need a grammar of language for parsing. Pyauparser use a .egt file which is
compiled from .grm file which consists of text-formatted grammar definitions.

You can write a .grm file with GOLD-Parser_ or alternatives with GOLD-Meta-Language_.
And instead of writing you can find lots of grammar files of popular languages at Grammars_.

.. _GOLD-Parser: http://www.goldparser.org
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

After preparing a .egt grammar file, we can load a grammar file now.
Load a grammar as following::

	g = pyauparser.Grammar.load_file("data/operator.egt")

Pyauparser doesn't support old .cgt file format.
But if you have a .grm file, you can make a .egt file with GOLD Parser 5 or newer.

Parse
-----

With a grammar, you can parse a string or a file. There are two way to handle parsing results.
First one is an event-driven way as following::

	def callback(ret, p):
	    if ret == pyauparser.parser.ParseResultType.SHIFT:
	        print "Shift\t{0}".format(p.top)
	    elif ret == pyauparser.parser.ParseResultType.REDUCE:
	        print "Reduce\t{0}".format(p.reduction)
	    elif ret == pyauparser.parser.ParseResultType.ACCEPT:
	        print "Accept\t{0}".format(p.top)
	    elif ret == pyauparser.parser.ParseResultType.ERROR:
	        print "Error\t{0}".format(p.error_info)
	
	pyauparser.parse_string(g, "-2*(3+4)-5", handler=callback)

Result is following::

	Shift	S=1, T=- '-'
	Shift	S=3, T=Num '2'
	Reduce	P=8, H=(S=8, P=<V> ::= Num), Hs=[(S=3, T=Num '2')]
	Reduce	P=6, H=(S=6, P=<N> ::= - <V>), Hs=[(S=1, T=- '-'), (S=8, P=<V> ::= Num)]
	Reduce	P=5, H=(S=5, P=<M> ::= <N>), Hs=[(S=6, P=<N> ::= - <V>)]
	...

It may look complicated but will be handled in a simple way.
Second one is creating a whole parse tree way as following::

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

As you see, a lookup-table is required to evaluate a value with parsing events.
Items in the table can be constructed by auparser with a grammar file as following::

	auparser.py show -P data/operator.egt

And you can get a following template table and modify it as you need::

	h = {
	    '<E> ::= <E> + <M>': None,
	    '<E> ::= <E> - <M>': None,
	    '<E> ::= <M>': None,
	    '<M> ::= <M> * <N>': None,
	    '<M> ::= <M> / <N>': None,
	    '<M> ::= <N>': None,
	    '<N> ::= - <V>': None,
	    '<N> ::= <V>': None,
	    '<V> ::= Num': None,
	    '<V> ::= ( <E> )': None,
	}

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

	auparser.py class data/operator.egt grammar_operator.py

We got grammar_operator.py. By import a grammar module and call load function grammar 
instance is created without an .egt file as following::

	import grammar_operator
	g = grammar_operator.load()

Link: https://github.com/veblush/PyAuParser/blob/master/sample/tutorial5.py

Changelog
=========

* 0.53

  * Fix auparser to work correctly under linux

* 0.52

  * Change arguments of parser event from top, reduction, error_info to a parser itself to
    simplify the interface
  * Change pname of symbol and production to id to clarify the meaning

* 0.51

  * Add a position field to Token class
  * Support non-unicode files

* 0.5

  * First release
