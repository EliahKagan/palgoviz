#!/usr/bin/env python

"""Calculator."""

import itertools
import operator

import graphviz

_OPERATORS = {'+': operator.add,
              '-': operator.sub,
              '*': operator.mul,
              '/': operator.truediv}


def postfix_calculate(expression):
    """
    Simplify a well-formed postfix arithmetic expression, returning a float.

    The expression consists of tokens separated by whitespace, where each token
    either can be interpreted as a floating-point number or is one of the
    symbols "+", "-", "*", or "/", denoting a binary arithmetic operation.

    In postfix notation, operands precede the operator that operates on them.

    >>> postfix_calculate('3')
    3.0
    >>> postfix_calculate('3 4 +')
    7.0
    >>> postfix_calculate('1 3 + 2 7 - /')
    -0.8
    >>> postfix_calculate('1 3 2 / + 7 -')
    -4.5
    >>> round(postfix_calculate('3 2.2 * 1 + 1 2 / -'), 10)
    7.1
    """
    operands = []

    for token in expression.split():
        try:
            operands.append(float(token))
        except ValueError:
            b = operands.pop()
            a = operands.pop()
            operands.append(_OPERATORS[token](a, b))

    return operands.pop()


class Result:
    """A leaf node in a binary expression tree."""

    __slots__ = ('_value',)

    __match_args__ = ('value',)

    def __init__(self, value):
        self._value = value

    def __repr__(self):
        return f'{type(self).__name__}({self.value!r})'

    @property
    def value(self):
        return self._value

    def evaluate(self):
        return self.value

    def serialize(self):
        return str(self.value)

    def simplify(self):
        return self


class Operation:
    """An internal node in a binary expression tree."""

    __slots__ = ('_symbol', '_left', '_right')

    __match_args__ = ('symbol', 'left', 'right')

    def __init__(self, symbol, left, right):
        self._symbol = symbol
        self._left = left
        self._right = right

    def __repr__(self):
        return (type(self).__name__
                + f'({self.symbol!r}, {self.left!r}, {self.right!r})')

    @property
    def symbol(self):
        return self._symbol

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right

    def evaluate(self):
        left_value = self.left.evaluate()
        right_value = self.right.evaluate()
        return _OPERATORS[self.symbol](left_value, right_value)

    def serialize(self):
        left_text = self.left.serialize()
        right_text = self.right.serialize()
        return f'{left_text} {right_text} {self.symbol}'

    def simplify(self):
        left = self.left.simplify()
        right = self.right.simplify()
        match _OPERATORS, left, right:
            case {self.symbol: op}, Result(left_value), Result(right_value):
                return Result(op(left_value, right_value))
            case _, self.left, self.right:
                return self
            case _, _, _:
                return Operation(self.symbol, left, right)


def parse(expression):
    """
    Convert a well-formed postfix expression to a binary expression tree.

    The expression consists of tokens separated by whitespace, where each token
    either can be interpreted as a floating-point number or an operator symbol.
    Even if the operator symbol is unrecognized, build the tree with it.
    """
    operands = []

    for token in expression.split():
        try:
            operands.append(Result(float(token)))
        except ValueError:
            right = operands.pop()
            left = operands.pop()
            operands.append(Operation(token, left, right))

    return operands.pop()


def draw(root):
    """
    Draw an expression tree as a Graphviz graph.

    Shade leaves light green and unrecognized operators pink.
    """
    graph = graphviz.Digraph()
    graph.node_attr['style'] = 'filled'
    names = map(str, itertools.count())

    def draw_branch(node):
        match node:
            case Result(value):
                name = next(names)
                graph.node(name, str(value), fillcolor='lightgreen')
            case Operation(symbol, left, right):
                left_name = draw_branch(left)
                right_name = draw_branch(right)
                name = next(names)
                fillcolor = ('white' if symbol in _OPERATORS else 'pink')
                graph.node(name, symbol, fillcolor=fillcolor)
                graph.edge(name, left_name)
                graph.edge(name, right_name)
            case _:
                raise TypeError(f'node must be Result or Operation, not '
                                + type(node).__name__)

        return name

    draw_branch(root)
    return graph


if __name__ == '__main__':
    import doctest
    doctest.testmod()
