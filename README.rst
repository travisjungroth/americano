Americano
=========

.. image:: https://circleci.com/gh/travisjungroth/americano/tree/master.svg?style=shield&circle-token=190bfe13ebf014f2598880d1369a802ebe8dda70
    :target: https://circleci.com/gh/travisjungroth/americano/tree/master

.. image:: https://coveralls.io/repos/github/travisjungroth/americano/badge.svg?branch=master
    :target: https://coveralls.io/github/travisjungroth/americano?branch=master

Americano is a parser and evaluator for a restricted subset of JavaScript, written in Python.

.. code-block:: python

    >>> from americano import parse
    >>> p = parse('var == 4')
    >>> p.eval({'var': 4})
    True
    >>> p.eval({'var': 5})
    False

The language accepted is a restricted subset of javascript.  The input must be an expression, not a statement.
The following operators are supported:
- ternary operator (?:)
- logical operators (||, &&)
- comparison operators (===, ==, !===, !=, <. <=, >, >=)
- addition/subtraction (+, -)
- multiplication/division (*, /)
- unary logical not (!)
- unary negation/plus (-, +)
- function invocation('(')
- computed member access ('[')
 
In addition, the following syntax constructs are supported:

- array literal
- null
- true
- false
- single quoted string
- double quoted string
- floating point literal (no exponential notation)
- integer literal

It is implemented using a variation of a Crockford TDOP style Pratt parser modified to support creation of an evaluable node tree on parse.

See these links for algorithm details:

- http://javascript.crockford.com/tdop/tdop.html
- http://eli.thegreenplace.net/2010/01/02/top-down-operator-precedence-parsing/
