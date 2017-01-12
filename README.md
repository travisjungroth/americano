Americano
=========

[![PyPI](https://img.shields.io/pypi/pyversions/americano.svg)](https://pypi.python.org/pypi/americano)
[![PyPI](https://img.shields.io/pypi/v/americano.svg)](https://pypi.python.org/pypi/americano)
[![CircleCI](https://circleci.com/gh/travisjungroth/americano.svg?style=shield)](https://circleci.com/gh/travisjungroth/americano)
[![Coveralls](https://coveralls.io/repos/github/travisjungroth/americano/badge.svg?branch=master)](https://coveralls.io/github/travisjungroth/americano?branch=master)

Americano is a parser and evaluator for a restricted subset of JavaScript, written in Python.

    >>> from americano import parse
    >>> p = parse('var == 4')
    >>> p.eval({'var': 4})
    True
    >>> p.eval({'var': 5})
    False

The language accepted is a restricted subset of javascript.  The input must be an expression, not a statement.
The following operators are supported:

 * ternary operator (?:)
 * logical operators (||, &&)
 * comparison operators (===, ==, !===, !=, <. <=, >, >=)
 * addition/subtraction (+, -)
 * multiplication/division (*, /)
 * unary logical not (!)
 * unary negation/plus (-, +)
 * function invocation('(')
 * computed member access ('[')
 
In addition, the following syntax constructs are supported:

 * array literal
 * null
 * true
 * false
 * single quoted string
 * double quoted string
 * floating point literal (no exponential notation)
 * integer literal

It is implemented using a variation of a Crockford TDOP style Pratt parser modified to support creation of an evaluable node tree on parse.

See these links for algorithm details:

 * http://javascript.crockford.com/tdop/tdop.html
 * http://eli.thegreenplace.net/2010/01/02/top-down-operator-precedence-parsing/

## Contributing
Pull requests must be up-to-date with master, and only squash merges are allowed.

The CI server checks:
 * The tests pass on the supported versions of Python using tox
 * Code coverage did not go down
 * Linting with [prospector](https://github.com/landscapeio/prospector)
    
To duplicate locally:

    pip install -r requirements/ci.txt
    tox
    prospector

You can probably get by with just running on one version of Python and letting the CI server handle the rest:

    pip install -r requirements/test.txt
    pytest --cov=americano
    prospector
