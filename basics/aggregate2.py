#!/usr/bin/env python3

"""
Named tuples and data classes: part 2 of 2: adding custom behavior.

This module picks up where aggregate1.py leaves off. aggregate1.py is about
various ways to aggregate data while implementing no, or few, special (dunder)
methods, and its examples are all close variations on a theme. In contrast,
this second module examines how named tuples and, more so, data classes, are
reasonable to use in some situations where greater custom behavior is called
for, either in construction, or of the constructed instance.
"""

from __future__ import annotations

import collections
from collections.abc import Iterator
import dataclasses
import math
import typing

import attrs


Coords = collections.namedtuple('Coords', ('x', 'y', 'z'))

Coords.__doc__ = """
    Named tuple of Cartesian coordinates in 3-space. Untyped. No inheritance.

    This is made using the type factory function in the collections module. Its
    intended use is as the return type for functions that will often have their
    results unpacked into multiple variable by an assignment at the call site,
    but may sometimes be retained in original form. Then it supports having its
    distance from the origin taken, by calling the abs builtin on it. (Even for
    objects that are not numbers, customizing abs is a common way to provide
    magnitude, so long as the magnitude is a number. Whether a Coords instance
    is being used to represent something with a magnitude varies by use case.)

    This implementation does not use inheritance, besides the inheritance from
    tuple that is taken care of by the type factory function. [FIXME: So no
    class statement will actually be involved here. This is just a way to give
    the docstring, which should be preserved and given to the type created by
    the type factory, and the class statement otherwise removed form the code.]

    >>> p = Coords(4, -12, 3)
    >>> p
    Coords(x=4, y=-12, z=3)
    >>> abs(p)
    13.0
    >>> isinstance(p, tuple), p.__slots__, hasattr(p, '__dict__')
    (True, (), False)
"""

Coords.__abs__ = lambda self: math.hypot(*self)
Coords.__abs__.__name__ = '__abs__'
Coords.__abs__.__qualname__ = f'{Coords.__name__}.{Coords.__abs__.__name__}'
Coords.__abs__.__doc__ = """The distance of this point from the origin."""


_CoordsAltBase = collections.namedtuple('_CoordsAltBase', ('x', 'y', 'z'))

_CoordsAltBase.__doc__ = """Private base class for CoordsAlt."""


class CoordsAlt(_CoordsAltBase):
    """
    Named tuple of Cartesian coordinates in 3-space. Untyped. By inheritance.

    This is like Coords, but it uses inheritance to add support for the abs
    builtin. Its non-public base class is created by the same factory function
    used to create Coords directly. (Neither Coords nor CoordsAlt inherits from
    the other and they do not depend on or use each other in any way.)

    >>> p = CoordsAlt(4, -12, 3)
    >>> p
    CoordsAlt(x=4, y=-12, z=3)
    >>> abs(p)
    13.0
    >>> isinstance(p, tuple), p.__slots__, hasattr(p, '__dict__')
    (True, (), False)
    """

    __slots__ = ()

    def __abs__(self):
        """The distance of this point from the origin."""
        return math.hypot(*self)


class TypedCoords(typing.NamedTuple):
    """
    Named tuple of Cartesian coordinates in 3-space. Has type annotations.

    This is like Coords/CoordsAlt but "typed." It is created with the facility
    in the typing module.

    >>> p = TypedCoords(4, -12, 3)
    >>> p
    TypedCoords(x=4, y=-12, z=3)
    >>> abs(p)
    13.0
    >>> isinstance(p, tuple), p.__slots__, hasattr(p, '__dict__')
    (True, (), False)
    """

    x: float
    y: float
    z: float

    def __abs__(self):
        """The distance of this point from the origin."""
        return math.hypot(*self)


class Point:
    """
    A point in 3-space, represented by its x-, y-, and z-coordinates.

    This is implemented as an attrs data class, with no type annotations, using
    the modern attrs API. Sometimes we use vectors to represent points, calling
    them positions or, to emphasize their vector nature, displacements. That is
    not what this is. Points have no magnitude, cannot be added to each other,
    and cannot be multiplied by scalars. They can be subtracted, though, which
    (geometrically speaking) is how vectors come into existence. The difference
    of two Point objects is a Vector object representing the displacement from
    the subtrahend to the minuend (so p - q points from q to p).

    FIXME: Needs tests.
    """
    # FIXME: Needs implementation.


class Vector:
    """
    A vector in 3-space, represented by its x-, y-, and z- components.

    FIXME: Needs description and tests.
    """
    # FIXME: Needs implementation.


class StrNode:
    """
    A node in a mutable singly linked list of strings, manually implemented.

    Both attributes are mutable. Both attributes, and all methods, have type
    annotations. Element types are not validated at runtime, so this could be
    used to store any kind of values, but static type checkers will report
    non-string values as errors. It's often better to make a generic Node type
    and use Node[str] instead of StrNode, but that is not done here. Also, the
    repr always shows both arguments, even if next=None, and it shows them as
    keyword arguments. This is all to make StrNode work like StrNodeA below,
    while still keeping the implementation of StrNodeA very straightforward.

    >>> StrNode('foo', StrNode('bar'))
    StrNode(value='foo', next=StrNode(value='bar', next=None))
    >>> StrNode.build('foo', 'bar')
    StrNode(value='foo', next=StrNode(value='bar', next=None))
    >>> _.value, _.next, _.next.value, _.next.next
    ('foo', StrNode(value='bar', next=None), 'bar', None)

    >>> head = StrNode('X')
    >>> head == StrNode('X')  # Not doing structural equality comparison.
    False
    >>> vars(head)  # No instance dictionary.
    Traceback (most recent call last):
      ...
    TypeError: vars() argument must have __dict__ attribute
    >>> import weakref; weakref.ref(head)  # No weak reference support.
    Traceback (most recent call last):
      ...
    TypeError: cannot create weak reference to 'StrNode' object

    >>> head.value = 'W'
    >>> head.next = StrNode.build('Y', 'Z')
    >>> head  # doctest: +NORMALIZE_WHITESPACE
    StrNode(value='W',
            next=StrNode(value='Y', next=StrNode(value='Z', next=None)))
    """

    __slots__ = ('value', 'next')

    value: str
    next: StrNode | None

    @classmethod
    def build(cls, *values: str) -> StrNode | None:
        """Make a singly linked list of the given values. Return the head."""
        acc = None
        for value in reversed(values):
            acc = cls(value, acc)
        return acc

    def __init__(self, value: str, next: StrNode | None = None) -> None:
        """Create a node with the given element value, and next node if any."""
        self.value = value
        self.next = next

    def __repr__(self) -> str:
        """Python code repr for debugging, using keyword arguments."""
        return (type(self).__name__
                + f'(value={self.value!r}, next={self.next!r})')


@attrs.mutable(eq=False, weakref_slot=False)
class StrNodeA:
    """
    A node in a mutable singly linked list of strings, as an attrs data class.

    This class uses the attrs library's modern API. It has type annotations.

    >>> StrNodeA('foo', StrNodeA('bar'))
    StrNodeA(value='foo', next=StrNodeA(value='bar', next=None))
    >>> StrNodeA.build('foo', 'bar')
    StrNodeA(value='foo', next=StrNodeA(value='bar', next=None))
    >>> _.value, _.next, _.next.value, _.next.next
    ('foo', StrNodeA(value='bar', next=None), 'bar', None)

    >>> head = StrNodeA('X')
    >>> head == StrNodeA('X')  # Not doing structural equality comparison.
    False
    >>> vars(head)  # No instance dictionary.
    Traceback (most recent call last):
      ...
    TypeError: vars() argument must have __dict__ attribute
    >>> import weakref; weakref.ref(head)  # No weak reference support.
    Traceback (most recent call last):
      ...
    TypeError: cannot create weak reference to 'StrNodeA' object

    >>> head.value = 'W'
    >>> head.next = StrNodeA.build('Y', 'Z')
    >>> head  # doctest: +NORMALIZE_WHITESPACE
    StrNodeA(value='W',
             next=StrNodeA(value='Y', next=StrNodeA(value='Z', next=None)))
    """

    value: str
    next: StrNodeA | None = None

    @classmethod
    def build(cls, *values: str) -> StrNodeA | None:
        """Make a singly linked list of the given values. Return the head."""
        acc = None
        for value in reversed(values):
            acc = cls(value, acc)
        return acc


@dataclasses.dataclass(slots=True, eq=False)
class StrNodeD:
    """
    A node in a mutable singly linked list of strings, as a @dataclass.

    This uses @dataclasses.dataclass, and therefore has type annotations.

    >>> StrNodeD('foo', StrNodeD('bar'))
    StrNodeD(value='foo', next=StrNodeD(value='bar', next=None))
    >>> StrNodeD.build('foo', 'bar')
    StrNodeD(value='foo', next=StrNodeD(value='bar', next=None))
    >>> _.value, _.next, _.next.value, _.next.next
    ('foo', StrNodeD(value='bar', next=None), 'bar', None)

    >>> head = StrNodeD('X')
    >>> head == StrNodeD('X')  # Not doing structural equality comparison.
    False
    >>> vars(head)  # No instance dictionary.
    Traceback (most recent call last):
      ...
    TypeError: vars() argument must have __dict__ attribute
    >>> import weakref; weakref.ref(head)  # No weak reference support.
    Traceback (most recent call last):
      ...
    TypeError: cannot create weak reference to 'StrNodeD' object

    >>> head.value = 'W'
    >>> head.next = StrNodeD.build('Y', 'Z')
    >>> head  # doctest: +NORMALIZE_WHITESPACE
    StrNodeD(value='W',
             next=StrNodeD(value='Y', next=StrNodeD(value='Z', next=None)))
    """

    value: str
    next: StrNodeD | None = None

    @classmethod
    def build(cls, *values: str) -> StrNodeD | None:
        """Make a singly linked list of the given values. Return the head."""
        acc = None
        for value in reversed(values):
            acc = cls(value, acc)
        return acc


def traverse(node: StrNode | StrNodeA | StrNodeD | None) -> Iterator[str]:
    """
    Yield all values in a singly linked list, from front to back.

    >>> import string

    >>> list(traverse(StrNode('foo', StrNode('bar'))))
    ['foo', 'bar']
    >>> list(traverse(StrNode.build('foo', 'bar')))
    ['foo', 'bar']
    >>> ','.join(traverse(StrNode.build(*string.ascii_lowercase)))
    'a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z'

    >>> list(traverse(StrNodeA('foo', StrNodeA('bar'))))
    ['foo', 'bar']
    >>> list(traverse(StrNodeA.build('foo', 'bar')))
    ['foo', 'bar']
    >>> ','.join(traverse(StrNodeA.build(*string.ascii_lowercase)))
    'a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z'

    >>> list(traverse(StrNodeD('foo', StrNodeD('bar'))))
    ['foo', 'bar']
    >>> list(traverse(StrNodeD.build('foo', 'bar')))
    ['foo', 'bar']
    >>> ','.join(traverse(StrNodeD.build(*string.ascii_lowercase)))
    'a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z'
    """
    while node:
        yield node.value
        node = node.next


__all__ = [thing.__name__ for thing in (  # type: ignore[attr-defined]
    Coords,
    CoordsAlt,
    TypedCoords,
    Point,
    Vector,
    StrNode,
    StrNodeA,
    StrNodeD,
    traverse,
)]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
