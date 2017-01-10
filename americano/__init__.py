from abc import ABCMeta, abstractmethod
from ast import literal_eval
from datetime import date
from numbers import Number
from operator import ge, gt, le, lt
import re
from six import string_types


def parse(expression, global_context=None):
    """
    Takes a string and returns a parsed expression, which can be evaluated with a context.

    >>> p = parse('var == 4')
    >>> p.eval({'var': 4})
    True
    >>> p.eval({'var': 5})
    False
    """
    return Parser(expression).root(global_context or {})


class ParseError(Exception):
    def __init__(self, message):
        super(ParseError, self).__init__(message)
        self.message = message


class EvaluationError(Exception):
    def __init__(self, message, cause=None):
        super(EvaluationError, self).__init__(message, cause)
        self.message = message
        self.cause = cause


# Helpers:
# Used internally while evaluating expressions

def coerce_to_bool(value):
    javascript_differences = [[], {}]
    return bool(value) ^ (value in javascript_differences)


def js_string(val):
    if val is None:
        return 'null'
    elif val is True:
        return 'true'
    elif val is False:
        return 'false'
    else:
        return str(val)


def js_number(val):
    """
    Converts val to a number if possible, else returns val.
    """
    if val is None or val is False:
        return 0
    elif val is True:
        return 1
    elif isinstance(val, string_types):
        if val.isdigit():
            return int(val)
        else:
            return float(val)
    else:
        return val


def add(left, right):
    if isinstance(left, string_types) or isinstance(right, string_types):
        return js_string(left) + js_string(right)
    else:
        return js_number(left) + js_number(right)


def sub(left, right):
    return js_number(left) - js_number(right)


def mul(left, right):
    return js_number(left) * js_number(right)


def div(left, right):
    return float(js_number(left)) / js_number(right)


def loose_equal(left, right):
    try:
        for a, b in ([left, right], [right, left]):
            if isinstance(a, str) and isinstance(b, Number):
                return literal_eval(a) == b
    except ValueError:
        return False
    else:
        return left == right


def loose_not_equal(left, right):
    return not loose_equal(left, right)


def strict_equal(left, right):
    same_type = type(left) is type(right)
    both_strings = all((isinstance(value, string_types) for value in [left, right]))
    both_numbers = all((isinstance(value, Number) and not isinstance(value, bool) for value in [left, right]))
    return (same_type or both_numbers or both_strings) and left == right


def strict_not_equal(left, right):
    return not strict_equal(left, right)


# Nodes:
#
# Nodes are the objects that are evaluated against a context to produce the value of an expression.
# The result of parsing an expression is the root Node of the expression that can then be evaluated.

class BaseNode(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def eval(self, context):
        raise NotImplementedError


class LiteralNode(BaseNode):
    def __init__(self, text):
        self.text = text

    def eval(self, context):
        return literal_eval(self.text)


class VariableReferenceNode(BaseNode):
    def __init__(self, name):
        self.name = name

    def eval(self, context):
        return context[self.name]


class TernaryOperatorNode(BaseNode):
    def __init__(self, condition_node, true_node, false_node):
        self.condition_node = condition_node
        self.true_node = true_node
        self.false_node = false_node

    def eval(self, context):
        val = self.condition_node.eval(context)
        return self.true_node.eval(context) if val else self.false_node.eval(context)


class BinaryOperatorNode(BaseNode):
    def __init__(self, first, second, op):
        self.first = first
        self.second = second
        self.op = op

    def eval(self, context):
        return self.op(self.first.eval(context), self.second.eval(context))


class AndBinaryOperatorNode(BaseNode):
    def __init__(self, first, second):
        self.first = first
        self.second = second

    def eval(self, context):
        first_value = self.first.eval(context)
        if not first_value:
            return first_value
        return self.second.eval(context)


class OrBinaryOperatorNode(BaseNode):
    def __init__(self, first, second):
        self.first = first
        self.second = second

    def eval(self, context):
        first_value = self.first.eval(context)
        if first_value:
            return first_value
        return self.second.eval(context)


class CoerceToNumberNode(BaseNode):
    def __init__(self, value_node, multiplier=1):
        self.value_node = value_node
        self.multiplier = multiplier

    def eval(self, context):
        value = self.value_node.eval(context)
        if value is None:
            return 0
        elif value is True:
            return 1 * self.multiplier
        elif value is False:
            return 0
        elif isinstance(value, date):
            raise EvaluationError('Conversion of date to number is unsupported')
        elif isinstance(value, int) or isinstance(value, float):
            return value * self.multiplier
        elif isinstance(value, str):
            try:
                parsed = int(value)
            except ValueError:
                try:
                    parsed = float(value)
                except ValueError:
                    return float('nan')
            return parsed * self.multiplier
        else:
            return float('nan')


class FunctionInvocationNode(BaseNode):
    def __init__(self, function_node, arg_nodes):
        self.function_node = function_node
        self.arg_nodes = arg_nodes

    def eval(self, context):
        f = self.function_node.eval(context)
        args = [arg_node.eval(context) for arg_node in self.arg_nodes]
        return f(*args)


class UnaryNegationNode(BaseNode):
    def __init__(self, value_node):
        self.value_node = value_node

    def eval(self, context):
        return not coerce_to_bool(self.value_node.eval(context))


class ArrayLiteralNode(BaseNode):
    def __init__(self, member_nodes):
        self.member_nodes = member_nodes

    def eval(self, context):
        return [member_node.eval(context) for member_node in self.member_nodes]


class ComputedAccessorNode(BaseNode):
    def __init__(self, object_node, accessor_node):
        self.object_node = object_node
        self.accessor_node = accessor_node

    def eval(self, context):
        obj = self.object_node.eval(context)
        return obj[self.accessor_node.eval(context)]


class RootNode(BaseNode):
    def __init__(self, expression_text, global_context, child_node):
        self.expression_text = expression_text
        self.global_context = global_context
        self.child_node = child_node

    def eval(self, context):
        try:
            merged_context = context.copy()
            merged_context.update(self.global_context)
            merged_context['true'] = True
            merged_context['false'] = False
            merged_context['null'] = None
            return self.child_node.eval(merged_context)
        except Exception as e:
            raise EvaluationError('Error evaluating expression {} with context {}: {}'.format(
                self.expression_text, repr(context), str(e)), e)


# Tokens:
#
# Tokens are the objects that are involved in parsing.  Each token contains functions and metadata to
# parse itself and children and construct a node tree
class BaseToken(object):
    lbp = 0

    def __init__(self, parser, text):
        self.parser = parser
        self.text = text

    def nud(self):
        raise ParseError('Token {} cannot be used in a null-denotation context'.format(self.text))

    def led(self, left):
        raise ParseError('Token {} cannot be used in a left-denotation context'.format(self.text))


class DelimiterToken(BaseToken):
    pass


class LiteralToken(BaseToken):
    def nud(self):
        return LiteralNode(self.text)


class VariableReferenceToken(BaseToken):
    def nud(self):
        return VariableReferenceNode(self.text)


class TernaryOperatorToken(BaseToken):
    lbp = 20

    def led(self, left):
        true_node = self.parser.expression(0)
        self.parser.advance(':')
        false_node = self.parser.expression(0)
        return TernaryOperatorNode(left, true_node, false_node)


class AndBinaryOperatorToken(BaseToken):
    lbp = 30

    def led(self, left):
        return AndBinaryOperatorNode(left, self.parser.expression(self.lbp - 1))


class OrBinaryOperatorToken(BaseToken):
    lbp = 30

    def led(self, left):
        return OrBinaryOperatorNode(left, self.parser.expression(self.lbp - 1))


class BinaryOperatorToken(BaseToken):
    @classmethod
    def factory(cls, bp, op):
        def new_instance(parser, text):
            return cls(parser, text, bp, op)
        return new_instance

    def __init__(self, parser, text, bp, op):
        self.lbp = bp
        self.op = op
        super(BinaryOperatorToken, self).__init__(parser, text)

    def led(self, left):
        return BinaryOperatorNode(left, self.parser.expression(self.lbp), self.op)


class PlusToken(BinaryOperatorToken):
    def nud(self):
        right = self.parser.expression(70)
        return CoerceToNumberNode(right)


class MinusToken(BinaryOperatorToken):
    def nud(self):
        right = self.parser.expression(70)
        return CoerceToNumberNode(right, multiplier=-1)


class UnaryNegationToken(BaseToken):
    def nud(self):
        return UnaryNegationNode(self.parser.expression(70))


class OpenParenToken(BaseToken):
    lbp = 80

    def nud(self):
        # Grouping operator: (...)
        e = self.parser.expression(0)
        self.parser.advance(')')
        return e

    def led(self, left):
        # Function invocation
        args = []
        if not self.parser.token_is(')'):
            while True:
                args.append(self.parser.expression(0))
                if not self.parser.token_is(','):
                    break
                self.parser.advance(',')
        self.parser.advance(')')
        return FunctionInvocationNode(left, args)


class OpenBracketToken(BaseToken):
    lbp = 80

    def nud(self):
        # Array literal: [...]
        members = []
        if not self.parser.token_is(']'):
            while True:
                members.append(self.parser.expression(0))
                if not self.parser.token_is(','):
                    break
                self.parser.advance(',')
                if self.parser.token_is(']'):  # [value,] is legal
                    break
        self.parser.advance(']')
        return ArrayLiteralNode(members)

    def led(self, left):
        # Computed member accessor a[b]
        node = ComputedAccessorNode(left, self.parser.expression(0))
        self.parser.advance(')')
        return node


SYMBOL_TABLE = {}


def register_symbol(text, token_factory):
    SYMBOL_TABLE[text] = token_factory


# Precedence 0: Non-binding operators
register_symbol(':', DelimiterToken)
register_symbol(',', DelimiterToken)
register_symbol(')', DelimiterToken)
register_symbol(']', DelimiterToken)

# Precedence 20: Ternary operator
register_symbol('?', TernaryOperatorToken)

# Precedence 30: Logical short-circuit operators
register_symbol('&&', AndBinaryOperatorToken)
register_symbol('||', OrBinaryOperatorToken)

# Precedence 40: relational operators
register_symbol('===', BinaryOperatorToken.factory(40, strict_equal))
register_symbol('!==', BinaryOperatorToken.factory(40, strict_not_equal))
register_symbol('==', BinaryOperatorToken.factory(40, loose_equal))
register_symbol('!=', BinaryOperatorToken.factory(40, loose_not_equal))
register_symbol('<', BinaryOperatorToken.factory(40, lt))
register_symbol('<=', BinaryOperatorToken.factory(40, le))
register_symbol('>', BinaryOperatorToken.factory(40, gt))
register_symbol('>=', BinaryOperatorToken.factory(40, ge))

# Precedence 50: plus, minus
register_symbol('-', MinusToken.factory(50, sub))
register_symbol('+', PlusToken.factory(50, add))

# Precedence 60: multiply, divide
register_symbol('*', BinaryOperatorToken.factory(60, mul))
register_symbol('/', BinaryOperatorToken.factory(60, div))

# Precedence 70: unary operators
# Note that unary plus and minus are registered previously
register_symbol('!', UnaryNegationToken)

# Precedence 80: function invocation, array dereference
# Note that ( and [ have null denotations for grouping and array literals respectively
register_symbol('(', OpenParenToken)
register_symbol('[', OpenBracketToken)


INPUT_TOKEN_PATTERNS = (
    ('name', (r'[a-zA-Z_$][a-zA-Z0-9_$]*',)),
    ('literal', (r'"(?:\\.|[^"])*"', r"'(?:\\.|[^'])*'", r'\d+\.\d+', r'\d+')),
    ('ws', (r'\s+',))
)


class Parser(object):
    """Contains the state related to parsing a single expression"""
    def __init__(self, expression):
        self.expression_text = expression
        self.token_itr = self.tokenize(expression)
        self.token = next(self.token_itr)

    def root(self, global_context):
        try:
            return RootNode(self.expression_text, global_context, self.expression(0))
        except ParseError as e:
            raise ParseError('Error parsing {}: {}'.format(self.expression_text, e.message))

    def tokenize(self, expression):
        handlers = {
            'name': lambda text: VariableReferenceToken(self, text),
            'literal': lambda text: LiteralToken(self, text),
            'operator': lambda text: SYMBOL_TABLE[text](self, text)
        }

        group_template = '(?P<{}>{})'
        parts = []
        for name, patterns in INPUT_TOKEN_PATTERNS:
            parts.append(group_template.format(name, '|'.join(patterns)))
        sorted_ops = [k for k in SYMBOL_TABLE.keys()]
        sorted_ops.sort(key=len, reverse=True)
        parts.append(group_template.format('operator', '|'.join((re.escape(v) for v in sorted_ops))))

        pattern = re.compile('|'.join(parts))
        mo = pattern.match(expression)
        while mo is not None:
            typ = mo.lastgroup
            if typ != 'ws':
                yield handlers[typ](mo.group(typ))
            pos = mo.end()
            mo = pattern.match(expression, pos)
        if pos != len(expression):
            raise RuntimeError('Cannot tokenize {}'.format(expression))
        yield DelimiterToken(self, '(end)')

    def expression(self, rbp):
        t = self.token
        self.token = next(self.token_itr)
        left = t.nud()
        while rbp < self.token.lbp:
            t = self.token
            self.token = next(self.token_itr)
            left = t.led(left)
        return left

    def advance(self, expected):
        t = self.token
        self.token = next(self.token_itr)
        if t.text != expected:
            raise RuntimeError('Expected {}'.format(expected))

    def token_is(self, expected):
        return self.token.text == expected
