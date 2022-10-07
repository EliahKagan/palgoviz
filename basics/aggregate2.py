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
from numbers import Real
from typing import Any, NamedTuple, cast

import attrs


def _coords_abs(self):
    """The distance of this point from the origin."""
    return math.hypot(*self)


_coords_abs.__name__ = '__abs__'
_coords_abs.__qualname__ = 'Coords.__abs__'


Coords = collections.namedtuple('Coords', ('x', 'y', 'z'))

Coords.__doc__ = """
    Named tuple of Cartesian coordinates in 3-space. Untyped. No inheritance.

    This is made using the type factory function in the collections module. Its
    intended use is as the return type for functions that will often have their
    results unpacked into multiple variables by an assignment at the call site,
    but may sometimes be retained in original form. Then it supports having its
    distance from the origin taken, by calling the abs builtin on it. (Even for
    objects that are not numbers, customizing abs is a common way to provide
    magnitude, so long as the magnitude is guaranteed to be a nonnegative real
    number. Whether a Coords instance is being used to represent something with
    a magnitude varies by use case.)

    This implementation does not use inheritance, besides the inheritance from
    tuple that is taken care of by the type factory function. It is still fine
    to inherit from this type, but that is not done in this module.

    [FIXME: No class statement will actually be involved here. This is just a
    place to put the docstring before the type is implemented. Give this
    docstring to the type the factory returns and remove this class statement.]

    >>> p = Coords(4, -12, 3)
    >>> p
    Coords(x=4, y=-12, z=3)
    >>> abs(p)
    13.0
    >>> isinstance(p, tuple), p.__slots__, hasattr(p, '__dict__')
    (True, (), False)
"""

cast(Any, Coords).__abs__ = _coords_abs


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


class TypedCoords(NamedTuple):
    """
    Named tuple of Cartesian coordinates in 3-space. Has type annotations.

    This is like Coords/CoordsAlt but "typed." It is created with the facility
    in the typing module for making named tuple types with typed attributes.

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

    def __abs__(self) -> float:
        """The distance of this point from the origin."""
        return math.hypot(*self)


_validate_real: Any = attrs.validators.instance_of(Real)
"""Helper runtime validator for real-valued arguments, for Point and Vector."""


@attrs.frozen
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

    Unlike Vector, where the object all of whose coordinates are zero is very
    special, what point we choose as the origin is just a matter of convention.
    So it is somewhat inelegant that Point allows omitting any combination of
    coordinate arguments on construction, with the same effect as passing 0.
    But it does, because this makes it much easier to use a Point to solve
    problems in a 1- or 2-dimensional coordinate system, by setting the other
    two or one coordinates, respectively, to zero, and ignoring them.

    Mathematical operations defined in the Point and Vector classes never
    return indirect instances of Point or Vector, even on operands that are
    instances of derived classes. There is no obviously best approach to such
    situations; this approach is chosen for simplicity and expressive clarity.
    Also, mathematical operations in both these classes use match-case instead
    of isinstance, whenever both branching by type and extracting attributes.

    >>> Point(1, 2, 3), Point(1, 2), Point(1)
    (Point(x=1, y=2, z=3), Point(x=1, y=2, z=0), Point(x=1, y=0, z=0))
    >>> Point(z=3), Point(1, z=3), Point(y=2, x=1)
    (Point(x=0, y=0, z=3), Point(x=1, y=0, z=3), Point(x=1, y=2, z=0))
    >>> {Point(0.0), Point(), Point(0, 0), Point(0.0, 0.0, 0.0)}
    {Point(x=0.0, y=0, z=0)}

    >>> from fractions import Fraction; Point(z=Fraction(1, 2), x=Fraction())
    Point(x=Fraction(0, 1), y=0, z=Fraction(1, 2))
    >>> Point(0j)  # Use attrs.validators.  # doctest +ELLIPSIS
    Traceback (most recent call last):
      ...
    TypeError: ("'x' must be <class 'numbers.Real'> ...", ...)

    >>> p = Point(3.1, -7, 5.0); q = Point(3.1, 1.6, 5)
    >>> p == Point(3.1, -7.0, 5), p == q, attrs.evolve(p, y=1.6) == q, p == q
    (True, False, True, False)
    >>> p.y = 1.6
    Traceback (most recent call last):
      ...
    attr.exceptions.FrozenInstanceError
    >>> p.t = -4  # No t attribute. This is not Minkowski space.
    Traceback (most recent call last):
      ...
    attr.exceptions.FrozenInstanceError

    >>> hasattr(p, '__dict__'), attrs.asdict(p)
    (False, {'x': 3.1, 'y': -7, 'z': 5.0})
    >>> abs(p)
    Traceback (most recent call last):
      ...
    TypeError: bad operand type for abs(): 'Point'
    >>> p.coords, p.coords == attrs.astuple(p), round(abs(p.coords), 5)
    (Coords(x=3.1, y=-7, z=5.0), True, 9.14385)

    >>> p - q, q - p
    (Vector(x=0.0, y=-8.6, z=0.0), Vector(x=0.0, y=8.6, z=0.0))
    >>> p + Vector(y=1.2), Vector(y=1.2) + p
    (Point(x=3.1, y=-5.8, z=5.0), Point(x=3.1, y=-5.8, z=5.0))
    >>> p - Vector(y=1.2)
    Point(x=3.1, y=-8.2, z=5.0)
    >>> Vector(y=1.2) - p  # We can't subtract a point from a vector.
    Traceback (most recent call last):
      ...
    TypeError: unsupported operand type(s) for -: 'Vector' and 'Point'
    >>> p + 3.14159  # It makes no sense to add a point and a scalar.
    Traceback (most recent call last):
      ...
    TypeError: unsupported operand type(s) for +: 'Point' and 'float'
    """

    x = attrs.field(default=0, validator=_validate_real)
    y = attrs.field(default=0, validator=_validate_real)
    z = attrs.field(default=0, validator=_validate_real)

    def __add__(self, addend):
        """
        Add a Point and a Vector, returning a Point.

        A Point and a Vector can be added in either order with the same effect.
        """
        match addend:
            case Vector(x, y, z):
                return Point(self.x + x, self.y + y, self.z + z)
            case _:
                return NotImplemented

    __radd__ = __add__

    def __sub__(self, subtrahend):
        """
        Subtract a Vector from this Point, or a Point from this Point.

        Subtracting a Vector from this Point returns a Point.

        Subtracting a Point from this Point returns a Vector.
        """
        match subtrahend:
            case Point(x, y, z):
                return Vector(self.x - x, self.y - y, self.z - z)
            case Vector(x, y, z):
                return Point(self.x - x, self.y - y, self.z - z)
            case _:
                return NotImplemented

    def __rsub__(self, minuend):
        """
        Subtract this Point from a Point, returning a Vector.

        Subtracting this Point from a Vector makes no sense and is not allowed.
        """
        match minuend:
            case Point(x, y, z):
                return Vector(x - self.x, y - self.y, z - self.z)
            case _:
                return NotImplemented

    @property
    def coords(self):
        """The coordinates of this Point, as a Coords name tuple object."""
        return Coords(self.x, self.y, self.z)


@attrs.frozen
class Vector:
    """
    A vector in 3-space, represented by its x-, y-, and z- components.

    Like Point, this is implemented as an attrs data class, with no type
    annotations, using the modern attrs API. Geometric vectors represent
    translations, also called displacements. Under this conceptualization, the
    meaning of a Vector object fundamentally relates to its ability to be added
    to a Point object to get another Point object. Vectors can also be added
    and subtracted from each other, multiplied by real-valued scalars, and
    divided by nonzero real-valued scalars, all of which return a Vector.

    There are two conceptually interesting things about Vector. First, notice
    that, while a Vector takes its meaning from the relationship it expresses
    between Points, there is no way to get a Point if you don't have one to
    start with (or the ability to explicitly call the Point type to make one).
    With just Points, we can get a Vector; with just Vectors, even scalars too,
    we cannot get a Point. Second, notice that the identity (a b) v = a (b v),
    where a and b are scalars and v is a vector, gives meaning to the operation
    of multiplying two scalars: composition of the dilation transformations
    they represent. So too, the identity p + (u + v) = (p + u) + v, where u and
    v are vectors and p is a point, gives meaning to the operation of adding
    two vectors: composition of the translation transformations they represent.

    Several aspects of choice of coordinate system are arbitrary, but there is
    nothing arbitrary about the zero Vector: it is the Vector that, when added
    to any Point, gives that same Point. More broadly, assuming prior choice of
    axes, it makes sense that if we don't want to displace along some axis, we
    would omit its component when constructing the Vector that represents the
    displacement we are doing. So, like Point, all arguments to Vector are
    optional; unlike Point, however, it is elegant that Vector allows this.

    >>> Vector(1, 2, 3), Vector(1, 2), Vector(1)
    (Vector(x=1, y=2, z=3), Vector(x=1, y=2, z=0), Vector(x=1, y=0, z=0))
    >>> Vector(z=3), Vector(1, z=3), Vector(y=2, x=1)
    (Vector(x=0, y=0, z=3), Vector(x=1, y=0, z=3), Vector(x=1, y=2, z=0))
    >>> {Vector(0.0), Vector(), Vector(0, 0), Vector(0.0, 0.0, 0.0)}
    {Vector(x=0.0, y=0, z=0)}

    >>> from fractions import Fraction; Vector(z=Fraction(1, 2), x=Fraction())
    Vector(x=Fraction(0, 1), y=0, z=Fraction(1, 2))
    >>> Vector(0j)  # Use attrs.validators.  # doctest +ELLIPSIS
    Traceback (most recent call last):
      ...
    TypeError: ("'x' must be <class 'numbers.Real'> ...", ...)

    >>> -Vector(1, 2, 3) + +Vector(4, 6, 8) - Vector(z=2.0)
    Vector(x=3, y=4, z=3.0)
    >>> 0.5 * Vector(1, 2, 3) * 0.5
    Vector(x=0.25, y=0.5, z=0.75)
    >>> round(abs(_), 5), round(abs(_ * 10), 5), round(abs(_ / 10), 5)
    (0.93541, 9.35414, 0.09354)

    >>> 1 / Vector(1, 2, 3)
    Traceback (most recent call last):
      ...
    TypeError: unsupported operand type(s) for /: 'int' and 'Vector'
    >>> Vector(1, 2, 3) / Vector(4, 5, 6)
    Traceback (most recent call last):
      ...
    TypeError: unsupported operand type(s) for /: 'Vector' and 'Vector'

    >>> p = Point(3.1, -7, 5.0); q = Point(3.1, 1.6, 5)
    >>> abs(p - q), round(abs(p - Point()), 5), round(abs(q - Point()), 5)
    (8.6, 9.14385, 6.09672)

    >>> i, j, k = Vector(x=1), Vector(y=1), Vector(z=1)
    >>> p - Point() == p.x * i + p.y * j + p.z * k
    True
    >>> hasattr(k, '__dict__'), attrs.asdict(k)
    (False, {'x': 0, 'y': 0, 'z': 1})
    """

    x = attrs.field(default=0, validator=_validate_real)
    y = attrs.field(default=0, validator=_validate_real)
    z = attrs.field(default=0, validator=_validate_real)

    def __add__(self, vector):
        """Add two Vectors, returning a Vector."""
        match vector:
            case Vector(x, y, z):
                return Vector(self.x + x, self.y + y, self.z + z)
            case _:
                return NotImplemented

    __radd__ = __add__

    def __sub__(self, vector):
        """Subtract a Vector from this Vector, returning a Vector."""
        match vector:
            case Vector(x, y, z):
                return Vector(self.x - x, self.y - y, self.z - z)
            case _:
                return NotImplemented

    def __rsub__(self, vector):
        """Subtract this vector from a Vector, returning a Vector."""
        match vector:
            case Vector(x, y, z):
                return Vector(x - self.x, y - self.y, z - self.z)
            case _:
                return NotImplemented

    def __mul__(self, scalar):
        """Multiply this Vector by a real number, returning a Vector."""
        if isinstance(scalar, Real):
            return Vector(self.x * scalar, self.y * scalar, self.z * scalar)
        return NotImplemented

    __rmul__ = __mul__

    def __truediv__(self, scalar):
        """Divide this Vector by a nonzero scalar, returning a Vector."""
        if isinstance(scalar, Real):
            return Vector(self.x / scalar, self.y / scalar, self.z / scalar)
        return NotImplemented

    def __neg__(self):
        """Compute a Vector of the magnitude as this but opposite direction."""
        return Vector(-self.x, -self.y, -self.z)

    def __pos__(self):
        """"Compute" a Vector with the same magnitude and direction as this."""
        # We're immutable, so it would be safe to just return self. Instead, we
        # return a new object, to ensure the result is always a direct instance
        # of Vector, for consistency with the other mathematical operations.
        return Vector(self.x, self.y, self.z)

    def __abs__(self):
        """Compute this Vector's magnitude, which is a nonnegative scalar."""
        return math.hypot(self.x, self.y, self.z)

    @property
    def coords(self):
        """The components of this Vector, as a Coords name tuple object."""
        return Coords(self.x, self.y, self.z)


class StrNode:
    """
    A node in a mutable singly linked list of strings, manually implemented.

    Both attributes are mutable. Both attributes, and all methods, have type
    annotations. Element types are not validated at runtime, so this could be
    used to store any kind of values, but static type checkers will report
    non-string values as errors.

    Though also not validated at runtime, it's often better to make a generic
    Node type and use Node[str] instead of StrNode, but that is not done here.
    Also, the repr always shows both arguments, even if next=None, and it shows
    them as keyword arguments. This is all so StrNode works like StrNodeA
    (below), while keeping the implementation of StrNodeA very straightforward.

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
