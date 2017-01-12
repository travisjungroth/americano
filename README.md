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
### Beginner
#### Forking
Follow [https://guides.github.com/activities/forking/](this guide) for forking the repository. Or, [this guide](http://kbroman.org/github_tutorial/pages/fork.html) if you're comfortable with the command line. 

#### Opening a Pull Request
When you open a pull request, your code is automatically loaded onto a Continuous Integration (CI) server. 

#### Making a Virtual Environment
You should make a virtual environment to create an isolated install of Python. You can use [virtualenv](https://virtualenv.pypa.io/en/stable/), but your life will be easier if you use [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) or [autoenv](https://github.com/kennethreitz/autoenv).

Once your virtual environment is active, install the requirements

    pip install -r requirements/test.txt

#### Running Tests
Americano uses [pytest](http://doc.pytest.org/en/latest/). The configuration is in `pytest.ini`, so you only need to run the test command. This will also run the doctests.

    pytest
    
#### Checking Coverage
To run the tests and see a coverage report:

    pytest --cov=americano
    
This uses [coverage](http://coverage.readthedocs.io/en/latest/) and [pytest-cov](http://pytest-cov.readthedocs.io/en/latest/).

#### Testing Multiple Versions
Calling `pytest` will test run the tests only against one version of Python. The CI server for Americano uses `tox` to test against all supported versions. To install multiple versions of Python, use [pyenv](https://github.com/yyuu/pyenv). Then, you can call tox and it will handle the testing just like the CI server.

    tox

#### Linting
_Linting_ is doing an analysis of the code file to check for mistakes. Americano uses [http://prospector.landscape.io/en/master/](http://prospector.landscape.io/en/master/), which calls a variety of other linting tools and passes in reasonable defaults.

    prospector





### Experienced
Pull requests must be up-to-date with master, and only squash merges are allowed.

The CI server checks:
 * The tests pass on the supported versions of Python using tox
 * Code coverage did not go down
 * Linting with [prospector](https://github.com/landscapeio/prospector)

To duplicate locally

    pip install -r requirements/dev.txt
    tox

You can probably get by with just running on one version of Python and letting the CI server handle the rest:

    pip install -r requirements/test.txt
    pytest --cov=americano
    prospector