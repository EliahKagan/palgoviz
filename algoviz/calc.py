#!/usr/bin/env python

"""
Calculator and expression trees.

The postfix_calculate function directly evaluates an arithmetic expression in
postfix notation. The other code here works with expression trees: building,
evaluating, simplifying, serializing (to postfix notation), and drawing.

An expression tree represents an expression. Subtrees represent subexpressions.
Internal nodes hold operators; leaves hold irreducible terms. In an algebraic
expression tree, internal nodes hold arithmetic operators and leaves hold
variables or constants. This module uses arithmetic expression trees, which are
algebraic expression trees but with variables prohibited. A manual drawing of
an arithmetic expression tree appears at the top of subproblems.ipynb and helps
show intuitively what an expression tree is. The draw function in this module
makes drawings like that, but with some specially significant nodes colorized.

In this module we regard each node to represent the entire subtree it roots,
and we use separate node types for internal nodes and leaves: the Compound and
Atom classes. Often one goes further than this, using a separate internal node
type for each operator, but we don't do that here, and we allow expressions
containing unrecognized operators to be represented (though of course we cannot
compute their values). In general, expression trees may support operators of
any arity, including operators of variable arity. But this module is concerned
only with binary expression trees, where each operator has an arity of 2, and
thus each internal node has exactly two children. Note that, unlike binary
trees in a general setting, nodes cannot have only one of their two children.

Comparing the implementations of postfix_calculate and postfix_parse reveals
the (perhaps surprising) similarity between evaluating a postfix expression and
transforming it into an expression tree.

Both serialization implementations (the postfix_serialize methods taken
together, and the alternative postfix_serialize_fast function) reveal the
connection between postfix notation and [FIXME: what kind of?] traversal.

Simplification builds a tree where evaluable branches are contracted to atoms:

>>> Compound('*', Compound('-', Atom(3), Atom(6)), Atom(2.25)).simplify()
Atom(-6.75)
>>> _.simplify() is _  # Atoms always simplify to the same object.
True

>>> postfix_parse('4 .25 + 1 2 / 3 ? -')  # doctest: +NORMALIZE_WHITESPACE
Compound('-', Compound('+', Atom(4.0), Atom(0.25)),
              Compound('?', Compound('/', Atom(1.0), Atom(2.0)), Atom(3.0)))
>>> _.simplify()
Compound('-', Atom(4.25), Compound('?', Atom(0.5), Atom(3.0)))
>>> _.simplify() is _  #  Irreducible Compounds simplify to the same object.
True

Simplification doesn't (currently) know algebraic rules for any operators:

>>> postfix_parse('1 2 + 3 4 @ + 5 6 + +')  # doctest: +NORMALIZE_WHITESPACE
Compound('+', Compound('+', Compound('+', Atom(1.0), Atom(2.0)),
                            Compound('@', Atom(3.0), Atom(4.0))),
              Compound('+', Atom(5.0), Atom(6.0)))
>>> _.simplify()  # doctest: +NORMALIZE_WHITESPACE
Compound('+', Compound('+', Atom(3.0), Compound('@', Atom(3.0), Atom(4.0))),
              Atom(11.0))

Nodes are "frozen" in the same sense as in tree.FrozenNode: attributes of Atom
and Compound objects may not be changed, created, or deleted (except by those
types' own initialization code, or by violating encapsulation). Since nodes
represent their entire subtrees, it would make sense to implement structural
equality comparison. But at least for now, Atom and Compound objects use
reference-based equality comparison, comparing equal only to themselves. This
is to avoid hiding how much (and what) work tree-processing code is doing.
"""

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
    can be interpreted as a floating-point number or is one of the symbols "+",
    "-", "*", or "/", denoting a binary arithmetic operation.

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


class Atom:
    """
    A leaf node in a binary expression tree.

    >>> atom = Atom(4.5)
    >>> atom
    Atom(4.5)
    >>> atom.value
    4.5
    >>> hasattr(atom, 'symbol'), hasattr(atom, 'left'), hasattr(atom, 'right')
    (False, False, False)
    >>> atom.evaluate()
    4.5
    >>> atom.postfix_serialize()
    '4.5'
    >>> atom.simplify()
    Atom(4.5)

    >>> Atom(4.0)
    Atom(4.0)
    >>> _.postfix_serialize()
    '4'

    See the module docstring for further doctests.
    """

    __slots__ = ('_value',)

    __match_args__ = ('value',)

    def __init__(self, value):
        self._value = value

    def __repr__(self):
        return f'{type(self).__name__}({self.value!r})'

    @property
    def value(self):
        """Compute the value of the expression this tree represents."""
        return self._value

    def evaluate(self):
        """Compute the value of the expression this tree represents."""
        return self.value

    def postfix_serialize(self):
        """Convert this expression tree to a postfix expression."""
        return str(self.value).removesuffix('.0')

    def simplify(self):
        """Build a copy with evaluable subtrees contracted to their results."""
        return self


class Compound:
    """
    An internal node in a binary expression tree.

    >>> compound = Compound('-', Compound('/', Atom(9), Atom(2)), Atom(0.5))
    >>> compound
    Compound('-', Compound('/', Atom(9), Atom(2)), Atom(0.5))
    >>> compound.symbol, compound.left, compound.right
    ('-', Compound('/', Atom(9), Atom(2)), Atom(0.5))
    >>> hasattr(compound, 'value')
    False
    >>> compound.evaluate()
    4.0
    >>> compound.postfix_serialize()
    '9 2 / 0.5 -'
    >>> compound.simplify()
    Atom(4.0)

    >>> Compound('+', Compound('*', Compound('-', Atom(1), Atom(2)),
    ...                             Compound('+', Atom(3), Atom(4))),
    ...               Compound('/', Compound('+', Atom(-5), Atom(1)),
    ...                             Compound('-', Atom(1),
    ...                                           Compound('/', Atom(63),
    ...                                                         Atom(64))))
    ... ).postfix_serialize()
    '1 2 - 3 4 + * -5 1 + 1 63 64 / - / +'

    See the module docstring for further doctests.

    FIXME: Ensure the postfix_serialize method's code as simple as possible,
    even though this means it is not as fast as possible. In its docstring,
    state its worst-case asymptotic time complexity, and mention the top-level
    postfix_serialize_fast function in case users want something faster.
    """

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
        """Compute the value of the expression this tree represents."""
        left_value = self.left.evaluate()
        right_value = self.right.evaluate()
        return _OPERATORS[self.symbol](left_value, right_value)

    def postfix_serialize(self):
        """Convert this expression tree to a postfix expression."""
        left_text = self.left.postfix_serialize()
        right_text = self.right.postfix_serialize()
        return f'{left_text} {right_text} {self.symbol}'

    def simplify(self):
        """Build a copy with evaluable subtrees contracted to their results."""
        left = self.left.simplify()
        right = self.right.simplify()
        match _OPERATORS, left, right:
            case {self.symbol: op}, Atom(left_value), Atom(right_value):
                return Atom(op(left_value, right_value))
            case _, self.left, self.right:
                return self
            case _, _, _:
                return Compound(self.symbol, left, right)


def postfix_parse(expression):
    """
    Convert a well-formed postfix expression to a binary expression tree.

    The expression consists of tokens separated by whitespace, where each token
    can be interpreted as a floating-point number or is an operator symbol.
    Even if the operator symbol is unrecognized, build the tree with it.

    >>> postfix_parse('3').evaluate()
    3.0
    >>> postfix_parse('3 4 +').evaluate()
    7.0
    >>> postfix_parse('1 3 + 2 7 - /').evaluate()
    -0.8
    >>> postfix_parse('1 3 2 / + 7 -').evaluate()
    -4.5
    >>> round(postfix_parse('3 2.2 * 1 + 1 2 / -').evaluate(), 10)
    7.1
    >>> postfix_parse('1 2 - 3 4 + * -5 1 + 1 63 64 / - / +'
    ...     )  # doctest: +NORMALIZE_WHITESPACE
    Compound('+', Compound('*', Compound('-', Atom(1.0), Atom(2.0)),
                                Compound('+', Atom(3.0), Atom(4.0))),
                  Compound('/', Compound('+', Atom(-5.0), Atom(1.0)),
                                Compound('-', Atom(1.0),
                                              Compound('/', Atom(63.0),
                                                            Atom(64.0)))))
    """
    operands = []

    for token in expression.split():
        try:
            operands.append(Atom(float(token)))
        except ValueError:
            right = operands.pop()
            left = operands.pop()
            operands.append(Compound(token, left, right))

    return operands.pop()


def postfix_serialize_fast(root):
    """
    Convert an expression tree to a postfix expression in linear time.

    >>> postfix_serialize_fast(postfix_parse('3'))
    '3'
    >>> postfix_serialize_fast(postfix_parse('3 4 +'))
    '3 4 +'
    >>> postfix_serialize_fast(postfix_parse('1 3 + 2 7 - /'))
    '1 3 + 2 7 - /'
    >>> postfix_serialize_fast(postfix_parse('3 2.2 * 1 + 1 2 / -'))
    '3 2.2 * 1 + 1 2 / -'
    >>> postfix_serialize_fast(
    ...     postfix_parse('1 2 - 3 4 + * -5 1 + 1 63 64 / - / +'))
    '1 2 - 3 4 + * -5 1 + 1 63 64 / - / +'
    """
    tokens = []

    def postorder(node):
        match node:
            case Atom(value):
                tokens.append(str(value).removesuffix('.0'))
            case Compound(symbol, left, right):
                postorder(left)
                postorder(right)
                tokens.append(symbol)

    postorder(root)
    return ' '.join(tokens)


def draw(root):
    """
    Draw an expression tree as a Graphviz graph.

    Shade leaves light green and unrecognized operators pink.

    Some drawings produced by this function can be seen in [FIXME: Make the
    drawings either in some existing notebook such as subproblems.ipynb or a
    new notebook. Give the notebook's filename here.]
    """
    graph = graphviz.Digraph()
    graph.node_attr['style'] = 'filled'
    names = map(str, itertools.count())

    def draw_branch(node):
        match node:
            case Atom(value):
                name = next(names)
                graph.node(name, str(value), fillcolor='lightgreen')
            case Compound(symbol, left, right):
                left_name = draw_branch(left)
                right_name = draw_branch(right)
                name = next(names)
                fillcolor = ('white' if symbol in _OPERATORS else 'pink')
                graph.node(name, symbol, fillcolor=fillcolor)
                graph.edge(name, left_name)
                graph.edge(name, right_name)
            case _:
                raise TypeError('node must be Atom or Compound, not '
                                + type(node).__name__)

        return name

    draw_branch(root)
    return graph


__all__ = [thing.__name__ for thing in (
    postfix_calculate,
    Atom,
    Compound,
    postfix_parse,
    postfix_serialize_fast,
    draw,
)]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
