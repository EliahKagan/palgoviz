#!/usr/bin/env python

"""Calculator."""

import operator

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
    # Build the list I want.
    tokens = expression.split()

    while len(tokens) > 1:
        # Find next operator w/o modifying the list.
        index, op = next((i, t) for i, t in enumerate(tokens) if t in _OPERATORS)

        a = float(tokens[index - 2])
        b = float(tokens[index - 1])
        result = _OPERATORS[op](a, b)

        tokens[index - 2 : index + 1] = (result,)

    return float(tokens.pop())
