#!/usr/bin/env python

"""Calculator."""

import operator

_OPERATORS = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
}


def postfix_calculate(expression):
    """
    Simplify a well-formed postfix arithmetic expression, returning a float.

    The expression consists of tokens separated by whitespace, where each token
    either can be interpreted as a floating-point number or is one of the
    symbols "+", "-", "*", or "/", denoting a binary arithmetic operation.

    In posfix notation, operands precede the operator that operates on them.

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
    stack = []

    for token in expression.split():
        try:
            stack.append(float(token))
        except ValueError:
            arg2 = stack.pop()
            arg1 = stack.pop()
            stack.append(_OPERATORS[token](arg1, arg2))

    if len(stack) != 1:
        raise ValueError('expression was ill-formed')

    return stack[0]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
