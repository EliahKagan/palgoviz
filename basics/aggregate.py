#!/usr/bin/env python3

"""
Named tuples and data classes.

This module starts with manual approaches to a problem of data aggregation that
is straightforward, yet (1) an imperfect fit for preexisting built-in and other
standard library types and (2) cumbersome to solve from scratch with explicitly
written special (dunder) methods. Named tuples and data classes solve it well.

Both named tuples and data classes (in the general sense that is not limited to
@dataclasses.dataclass) are presented here, with and without type annotations.
Because the attrs library fully supports both "typed" and "untyped" usage, and
it is a very popular and important library, a major focus here is on attrs data
classes. However, the standard library dataclasses module is shown, too.

Readers experienced in the Python data model can reimplement the functions and
classes in this module as exercises to learn about named tuples, data classes,
and the very basics of type annotations. However, readers with no familiarity
with any of those three topics might be well served to learn a little about at
least one, first. The material in this project that is intended as a first
introduction to named tuples and data classes appears in classes3.ipynb.

A goal of this module is to show alternatives, so code is freely duplicated
across functions, and across classes, when sharing it would obscure anything or
make any alternative less self contained -- except where noted otherwise.
"""

import collections
from collections.abc import Iterable
import math
import types
import typing

import attrs

DEFAULT_PRECISION = 5
"""How many fractional digits summarize* functions keep when rounding means."""


# FIXME: After implementing this and getting all tests to pass, run flake8 on
# the module before continuing. To facilitate side-by-side comparison, most of
# the other functions in this module will contain very similar code to the code
# here, most of which can and should be copied and pasted. But even though code
# duplication might be justified in this specific situation, its disadvantages
# still apply. It is easier to make improvements in one place than in many.
def summarize_as_tuple(values, *, precision=DEFAULT_PRECISION):
    """
    Compute min, max, and arithmetic, geometric, and harmonic mean.

    values is an arbitrary nonempty iterable of strictly positive real numbers.
    If values is empty, or any value is nonpositive, ValueError is raised. The
    caller is responsible for ensuring each object in values represents a real
    number. Means are given with the specified number of digits of precision.
    The five computed results are returned as a (non-named) tuple.

    All computations are done in a single pass: values is iterated just once.
    Time complexity is O(len(values)). Space complexity is O(1). These assume a
    number takes O(1) space and arithmetic operations take O(1) time, which is
    often an approximation in Python, but it is guaranteed when using floats.

    Other functions in this module, when documented with the phrase "This is
    like summarize_as_tuple," likewise make only one pass over their input and
    have the same time and space complexities as this, if not otherwise stated.

    >>> summarize_as_tuple([1, 3, 2.5, 3, 4])
    (1, 4, 2.7, 2.45951, 2.15827)

    >>> len({summarize_as_tuple([1, 3, 2.5, 3, 4]),
    ...      summarize_as_tuple([1, 3, 3, 2.5, 4]),
    ...      summarize_as_tuple([1, 2, 16, 4, 8])})
    2

    >>> _, _, am, _, _ = summarize_as_tuple([1, 2, 16, 4, 8])
    >>> am
    6.2

    >>> match summarize_as_tuple([1, 2, 16, 4, 8]):
    ...     case _, _, _, 4, hm:
    ...         print(f'Geometric mean four, harmonic mean {hm}.')
    Geometric mean four, harmonic mean 2.58065.
    """
    count = 0
    minimum = math.inf
    maximum = 0
    total = 0
    product = 1
    reciprocals_total = 0

    for value in values:
        if value <= 0:
            raise ValueError(f'nonpositive value {value!r}')

        count += 1
        minimum = min(minimum, value)
        maximum = max(maximum, value)
        total += value
        product *= value
        reciprocals_total += 1 / value

    if count == 0:
        raise ValueError('no values')

    arithmetic_mean = round(total / count, precision)
    geometric_mean = round(product**(1 / count), precision)
    harmonic_mean = round(count / reciprocals_total, precision)
    return minimum, maximum, arithmetic_mean, geometric_mean, harmonic_mean


def summarize_as_dict(values, *, precision=DEFAULT_PRECISION):
    """
    Compute min, max, and arithmetic, geometric, and harmonic mean.

    This is like summarize_as_tuple, but the computed results are returned as a
    dict.

    >>> s = summarize_as_dict([1, 3, 2.5, 3, 4])

    >>> s  # doctest: +NORMALIZE_WHITESPACE
    {'minimum': 1,
     'maximum': 4,
     'arithmetic mean': 2.7,
     'geometric mean': 2.45951,
     'harmonic mean': 2.15827}

    >>> hash(s)
    Traceback (most recent call last):
      ...
    TypeError: unhashable type: 'dict'

    >>> s == summarize_as_dict([1, 3, 3, 2.5, 4])
    True
    >>> s == summarize_as_dict([1, 2, 16, 4, 8])
    False

    >>> match summarize_as_dict([1, 2, 16, 4, 8]):
    ...     case {'geometric mean': 4, 'harmonic mean': hm}:
    ...         print(f'Geometric mean four, harmonic mean {hm}.')
    Geometric mean four, harmonic mean 2.58065.
    """
    count = 0
    minimum = math.inf
    maximum = 0
    total = 0
    product = 1
    reciprocals_total = 0

    for value in values:
        if value <= 0:
            raise ValueError(f'nonpositive value {value!r}')

        count += 1
        minimum = min(minimum, value)
        maximum = max(maximum, value)
        total += value
        product *= value
        reciprocals_total += 1 / value

    if count == 0:
        raise ValueError('no values')

    return {
        'minimum': minimum,
        'maximum': maximum,
        'arithmetic mean': round(total / count, precision),
        'geometric mean': round(product**(1 / count), precision),
        'harmonic mean': round(count / reciprocals_total, precision),
    }


def summarize_as_simple_namespace(values, *, precision=DEFAULT_PRECISION):
    """
    Compute min, max, and arithmetic, geometric, and harmonic mean.

    This is like summarize_as_tuple, but the five computed results are returned
    as a SimpleNamespace.

    >>> s = summarize_as_simple_namespace([1, 3, 2.5, 3, 4])

    >>> s  # doctest: +NORMALIZE_WHITESPACE
    namespace(minimum=1,
              maximum=4,
              arithmetic_mean=2.7,
              geometric_mean=2.45951,
              harmonic_mean=2.15827)

    >>> hash(s)
    Traceback (most recent call last):
      ...
    TypeError: unhashable type: 'types.SimpleNamespace'

    >>> s == summarize_as_simple_namespace([1, 3, 3, 2.5, 4])
    True
    >>> s == summarize_as_simple_namespace([1, 2, 16, 4, 8])
    False
    >>> s.minimum = 1.5; s == summarize_as_simple_namespace([1, 3, 2.5, 3, 4])
    False

    >>> match summarize_as_simple_namespace([1, 2, 16, 4, 8]):
    ...     case types.SimpleNamespace(geometric_mean=4, harmonic_mean=hm):
    ...         print(f'Geometric mean four, harmonic mean {hm}.')
    Geometric mean four, harmonic mean 2.58065.
    """
    count = 0
    minimum = math.inf
    maximum = 0
    total = 0
    product = 1
    reciprocals_total = 0

    for value in values:
        if value <= 0:
            raise ValueError(f'nonpositive value {value!r}')

        count += 1
        minimum = min(minimum, value)
        maximum = max(maximum, value)
        total += value
        product *= value
        reciprocals_total += 1 / value

    if count == 0:
        raise ValueError('no values')

    return types.SimpleNamespace(
        minimum=minimum,
        maximum=maximum,
        arithmetic_mean=round(total / count, precision),
        geometric_mean=round(product**(1 / count), precision),
        harmonic_mean=round(count / reciprocals_total, precision),
    )


class MyMutableSummary:
    """Mutable summary returned by summarize_as_mutable."""

    __slots__ = __match_args__ = (
        'minimum',
        'maximum',
        'arithmetic_mean',
        'geometric_mean',
        'harmonic_mean',
    )

    def __init__(self,
                 minimum,
                 maximum,
                 arithmetic_mean,
                 geometric_mean,
                 harmonic_mean):
        """Create a summary to report the given extrema and means."""
        self.minimum = minimum
        self.maximum = maximum
        self.arithmetic_mean = arithmetic_mean
        self.geometric_mean = geometric_mean
        self.harmonic_mean = harmonic_mean

    def __repr__(self):
        """Python code representation for debugging."""
        return (f'{type(self).__name__}('
                f'minimum={self.minimum!r}, '
                f'maximum={self.maximum!r}, '
                f'arithmetic_mean={self.arithmetic_mean!r}, '
                f'geometric_mean={self.geometric_mean!r}, '
                f'harmonic_mean={self.harmonic_mean!r})')

    def __eq__(self, other):
        """Instances are equal if they report the same corresponding values."""
        if not isinstance(other, type(self)):
            return NotImplemented

        return (self.minimum == other.minimum and
                self.maximum == other.maximum and
                self.arithmetic_mean == other.arithmetic_mean and
                self.geometric_mean == other.geometric_mean and
                self.harmonic_mean == other.harmonic_mean)


def summarize_as_mutable(values, *, precision=DEFAULT_PRECISION):
    """
    Compute min, max, and arithmetic, geometric, and harmonic mean.

    This is like summarize_as_tuple, but the five computed results are returned
    as an instance of a custom mutable slotted class, with all needed special
    methods implemented explicitly.

    >>> s = summarize_as_mutable([1, 3, 2.5, 3, 4])

    >>> s  # doctest: +NORMALIZE_WHITESPACE
    MyMutableSummary(minimum=1,
                     maximum=4,
                     arithmetic_mean=2.7,
                     geometric_mean=2.45951,
                     harmonic_mean=2.15827)

    >>> hash(s)
    Traceback (most recent call last):
      ...
    TypeError: unhashable type: 'MyMutableSummary'

    >>> s == summarize_as_mutable([1, 3, 3, 2.5, 4])
    True
    >>> s == summarize_as_mutable([1, 2, 16, 4, 8])
    False
    >>> s.minimum = 1.5; s == summarize_as_mutable([1, 3, 2.5, 3, 4])
    False

    >>> _, _, am, _, _ = summarize_as_mutable([1, 2, 16, 4, 8])
    Traceback (most recent call last):
      ...
    TypeError: cannot unpack non-iterable MyMutableSummary object

    >>> match summarize_as_mutable([1, 2, 16, 4, 8]):
    ...     case MyMutableSummary(geometric_mean=4, harmonic_mean=hm_kwd):
    ...         print(f'Geometric mean four, harmonic mean {hm_kwd}.')
    Geometric mean four, harmonic mean 2.58065.

    >>> match summarize_as_mutable([1, 2, 16, 4, 8]):
    ...     case MyMutableSummary(_, _, _, 4, hm_pos):
    ...         print(f'Geometric mean four, harmonic mean {hm_pos}.')
    Geometric mean four, harmonic mean 2.58065.
    """
    count = 0
    minimum = math.inf
    maximum = 0
    total = 0
    product = 1
    reciprocals_total = 0

    for value in values:
        if value <= 0:
            raise ValueError(f'nonpositive value {value!r}')

        count += 1
        minimum = min(minimum, value)
        maximum = max(maximum, value)
        total += value
        product *= value
        reciprocals_total += 1 / value

    if count == 0:
        raise ValueError('no values')

    return MyMutableSummary(
        minimum=minimum,
        maximum=maximum,
        arithmetic_mean=round(total / count, precision),
        geometric_mean=round(product**(1 / count), precision),
        harmonic_mean=round(count / reciprocals_total, precision),
    )


class MyMutableSummaryUnpack(MyMutableSummary):
    """
    Mutable summary returned by summarize_as_mutable_instance_unpack.

    This is like MyMutableSummary, but iterable so it can be unpacked into
    multiple variables on the left side of an assignment. Since interesting
    differences are limited to just one method, and replicating the entirety of
    MyMutableSummary would be distracting, this just inherits and adds it.
    """

    __slots__ = ()

    def __iter__(self):
        """Yield values in positional-argument order to allow unpacking."""
        yield self.minimum
        yield self.maximum
        yield self.arithmetic_mean
        yield self.geometric_mean
        yield self.harmonic_mean


def summarize_as_mutable_unpack(values, *, precision=DEFAULT_PRECISION):
    """
    Compute min, max, and arithmetic, geometric, and harmonic mean.

    This is like summarize_as_tuple, but the five computed results are returned
    as an instance of a custom mutable slotted class, capable of unpacking into
    its constituent values when assigned to multiple variables, with all needed
    special methods implemented explicitly.

    MyMutableSummary and MyMutableSummaryUnpack differ only by a single method.
    To repeat the rest of their code would obscure that. So one inherits from
    the other. This is an exception to the usual practice in this module.

    >>> s = summarize_as_mutable_unpack([1, 3, 2.5, 3, 4])

    >>> s  # doctest: +NORMALIZE_WHITESPACE
    MyMutableSummaryUnpack(minimum=1,
                           maximum=4,
                           arithmetic_mean=2.7,
                           geometric_mean=2.45951,
                           harmonic_mean=2.15827)

    >>> hash(s)
    Traceback (most recent call last):
      ...
    TypeError: unhashable type: 'MyMutableSummaryUnpack'

    >>> s == summarize_as_mutable_unpack([1, 3, 3, 2.5, 4])
    True
    >>> s == summarize_as_mutable_unpack([1, 2, 16, 4, 8])
    False
    >>> s.minimum = 1.5; s == summarize_as_mutable_unpack([1, 3, 2.5, 3, 4])
    False

    >>> _, _, am, _, _ = summarize_as_mutable_unpack([1, 2, 16, 4, 8])
    >>> am
    6.2

    >>> match summarize_as_mutable_unpack([1, 2, 16, 4, 8]):
    ...     case MyMutableSummaryUnpack(geometric_mean=4,
    ...                                 harmonic_mean=hm_kwd):
    ...         print(f'Geometric mean four, harmonic mean {hm_kwd}.')
    Geometric mean four, harmonic mean 2.58065.

    >>> match summarize_as_mutable_unpack([1, 2, 16, 4, 8]):
    ...     case MyMutableSummaryUnpack(_, _, _, 4, hm_pos):
    ...         print(f'Geometric mean four, harmonic mean {hm_pos}.')
    Geometric mean four, harmonic mean 2.58065.
    """
    count = 0
    minimum = math.inf
    maximum = 0
    total = 0
    product = 1
    reciprocals_total = 0

    for value in values:
        if value <= 0:
            raise ValueError(f'nonpositive value {value!r}')

        count += 1
        minimum = min(minimum, value)
        maximum = max(maximum, value)
        total += value
        product *= value
        reciprocals_total += 1 / value

    if count == 0:
        raise ValueError('no values')

    return MyMutableSummaryUnpack(
        minimum=minimum,
        maximum=maximum,
        arithmetic_mean=round(total / count, precision),
        geometric_mean=round(product**(1 / count), precision),
        harmonic_mean=round(count / reciprocals_total, precision),
    )


class MyFrozenSummary:
    """Immutable summary returned by summarize_as_frozen."""

    __slots__ = (
        '_minimum',
        '_maximum',
        '_arithmetic_mean',
        '_geometric_mean',
        '_harmonic_mean',
    )

    __match_args__ = (
        'minimum',
        'maximum',
        'arithmetic_mean',
        'geometric_mean',
        'harmonic_mean',
    )

    def __init__(self,
                 minimum,
                 maximum,
                 arithmetic_mean,
                 geometric_mean,
                 harmonic_mean):
        """Create a summary to report the given extrema and means."""
        self._minimum = minimum
        self._maximum = maximum
        self._arithmetic_mean = arithmetic_mean
        self._geometric_mean = geometric_mean
        self._harmonic_mean = harmonic_mean

    def __repr__(self):
        """Python code representation for debugging."""
        return (f'{type(self).__name__}('
                f'minimum={self.minimum!r}, '
                f'maximum={self.maximum!r}, '
                f'arithmetic_mean={self.arithmetic_mean!r}, '
                f'geometric_mean={self.geometric_mean!r}, '
                f'harmonic_mean={self.harmonic_mean!r})')

    def __eq__(self, other):
        """Instances are equal if they report the same corresponding values."""
        if not isinstance(other, type(self)):
            return NotImplemented

        return (self.minimum == other.minimum and
                self.maximum == other.maximum and
                self.arithmetic_mean == other.arithmetic_mean and
                self.geometric_mean == other.geometric_mean and
                self.harmonic_mean == other.harmonic_mean)

    def __hash__(self):
        return hash((self.minimum,
                     self.maximum,
                     self.arithmetic_mean,
                     self.geometric_mean,
                     self.harmonic_mean))

    @property
    def minimum(self):
        return self._minimum

    @property
    def maximum(self):
        return self._maximum

    @property
    def arithmetic_mean(self):
        return self._arithmetic_mean

    @property
    def geometric_mean(self):
        return self._geometric_mean

    @property
    def harmonic_mean(self):
        return self._harmonic_mean


def summarize_as_frozen(values, *, precision=DEFAULT_PRECISION):
    """
    Compute min, max, and arithmetic, geometric, and harmonic mean.

    This is like summarize_as_tuple, but the five computed results are returned
    as an instance of a custom immutable slotted class, with all needed special
    methods implemented explicitly.

    >>> s = summarize_as_frozen([1, 3, 2.5, 3, 4])

    >>> s  # doctest: +NORMALIZE_WHITESPACE
    MyFrozenSummary(minimum=1,
                    maximum=4,
                    arithmetic_mean=2.7,
                    geometric_mean=2.45951,
                    harmonic_mean=2.15827)

    >>> len({s, summarize_as_frozen([1, 3, 3, 2.5, 4]),
    ...      summarize_as_frozen([1, 2, 16, 4, 8])})
    2

    >>> s.minimum = 1.5
    Traceback (most recent call last):
      ...
    AttributeError: can't set attribute 'minimum'

    >>> _, _, am, _, _ = summarize_as_frozen([1, 2, 16, 4, 8])
    Traceback (most recent call last):
      ...
    TypeError: cannot unpack non-iterable MyFrozenSummary object

    >>> match summarize_as_frozen([1, 2, 16, 4, 8]):
    ...     case MyFrozenSummary(geometric_mean=4, harmonic_mean=hm_kwd):
    ...         print(f'Geometric mean four, harmonic mean {hm_kwd}.')
    Geometric mean four, harmonic mean 2.58065.

    >>> match summarize_as_frozen([1, 2, 16, 4, 8]):
    ...     case MyFrozenSummary(_, _, _, 4, hm_pos):
    ...         print(f'Geometric mean four, harmonic mean {hm_pos}.')
    Geometric mean four, harmonic mean 2.58065.
    """
    count = 0
    minimum = math.inf
    maximum = 0
    total = 0
    product = 1
    reciprocals_total = 0

    for value in values:
        if value <= 0:
            raise ValueError(f'nonpositive value {value!r}')

        count += 1
        minimum = min(minimum, value)
        maximum = max(maximum, value)
        total += value
        product *= value
        reciprocals_total += 1 / value

    if count == 0:
        raise ValueError('no values')

    return MyFrozenSummary(
        minimum=minimum,
        maximum=maximum,
        arithmetic_mean=round(total / count, precision),
        geometric_mean=round(product**(1 / count), precision),
        harmonic_mean=round(count / reciprocals_total, precision),
    )


class MyFrozenSummaryUnpack(MyFrozenSummary):
    """
    Immutable summary returned by summarize_as_frozen_unpack.

    This is like MyFrozenSummary, but iterable so it can be unpacked into
    multiple variables on the left side of an assignment. Since interesting
    differences are limited to just one method, and replicating the entirety of
    MyFrozenSummary would be distracting, this just inherits and adds it.
    """

    __slots__ = ()

    def __iter__(self):
        """Yield values in positional-argument order to allow unpacking."""
        yield self.minimum
        yield self.maximum
        yield self.arithmetic_mean
        yield self.geometric_mean
        yield self.harmonic_mean


def summarize_as_frozen_unpack(values, *, precision=DEFAULT_PRECISION):
    """
    Compute min, max, and arithmetic, geometric, and harmonic mean.

    This is like summarize_as_tuple, but the five computed results are returned
    as an instance of a custom immutable slotted class, capable of unpacking
    into its constituent values when assigned to multiple variables, with all
    needed special methods implemented explicitly.

    MyFrozenSummary and MyFrozenSummaryUnpack differ only by a single method.
    To repeat the rest of their code would obscure that. So one inherits from
    the other. This is an exception to the usual practice in this module.

    >>> s = summarize_as_frozen_unpack([1, 3, 2.5, 3, 4])

    >>> s  # doctest: +NORMALIZE_WHITESPACE
    MyFrozenSummaryUnpack(minimum=1,
                          maximum=4,
                          arithmetic_mean=2.7,
                          geometric_mean=2.45951,
                          harmonic_mean=2.15827)

    >>> len({s, summarize_as_frozen_unpack([1, 3, 3, 2.5, 4]),
    ...      summarize_as_frozen_unpack([1, 2, 16, 4, 8])})
    2

    >>> s.minimum = 1.5
    Traceback (most recent call last):
      ...
    AttributeError: can't set attribute 'minimum'

    >>> _, _, am, _, _ = summarize_as_frozen_unpack([1, 2, 16, 4, 8])
    >>> am
    6.2

    >>> match summarize_as_frozen_unpack([1, 2, 16, 4, 8]):
    ...     case MyFrozenSummaryUnpack(geometric_mean=4, harmonic_mean=hm_kwd):
    ...         print(f'Geometric mean four, harmonic mean {hm_kwd}.')
    Geometric mean four, harmonic mean 2.58065.

    >>> match summarize_as_frozen_unpack([1, 2, 16, 4, 8]):
    ...     case MyFrozenSummaryUnpack(_, _, _, 4, hm_pos):
    ...         print(f'Geometric mean four, harmonic mean {hm_pos}.')
    Geometric mean four, harmonic mean 2.58065.
    """
    count = 0
    minimum = math.inf
    maximum = 0
    total = 0
    product = 1
    reciprocals_total = 0

    for value in values:
        if value <= 0:
            raise ValueError(f'nonpositive value {value!r}')

        count += 1
        minimum = min(minimum, value)
        maximum = max(maximum, value)
        total += value
        product *= value
        reciprocals_total += 1 / value

    if count == 0:
        raise ValueError('no values')

    return MyFrozenSummaryUnpack(
        minimum=minimum,
        maximum=maximum,
        arithmetic_mean=round(total / count, precision),
        geometric_mean=round(product**(1 / count), precision),
        harmonic_mean=round(count / reciprocals_total, precision),
    )


class MyNamedTupleSummary(tuple):
    """
    Manual named tuple summary returned by summarize_as_manual_named_tuple.

    This is immutable and iterable, because tuples are.
    """

    __slots__ = ()

    __match_args__ = (
        'minimum',
        'maximum',
        'arithmetic_mean',
        'geometric_mean',
        'harmonic_mean',
    )

    def __new__(cls,
                minimum,
                maximum,
                arithmetic_mean,
                geometric_mean,
                harmonic_mean):
        """Create a summary to report the given extrema and means."""
        return super().__new__(cls, (
            minimum,
            maximum,
            arithmetic_mean,
            geometric_mean,
            harmonic_mean,
        ))

    def __repr__(self):
        """Python code representation for debugging."""
        return (f'{type(self).__name__}('
                f'minimum={self.minimum!r}, '
                f'maximum={self.maximum!r}, '
                f'arithmetic_mean={self.arithmetic_mean!r}, '
                f'geometric_mean={self.geometric_mean!r}, '
                f'harmonic_mean={self.harmonic_mean!r})')

    @property
    def minimum(self):
        return self[0]

    @property
    def maximum(self):
        return self[1]

    @property
    def arithmetic_mean(self):
        return self[2]

    @property
    def geometric_mean(self):
        return self[3]

    @property
    def harmonic_mean(self):
        return self[4]


def summarize_as_manual_named_tuple(values, *, precision=DEFAULT_PRECISION):
    """
    Compute min, max, and arithmetic, geometric, and harmonic mean.

    This is like summarize_as_tuple, but the five computed results are returned
    as an instance of a custom named tuple class: a class that inherits from
    tuple and extends it so elements can also be accessed by named attributes.
    For example, if summary is returned, summary.harmonic_mean accesses the
    same element summary[4] and summary[-1] access. Subscripting still works.

    Derived classes do not, as a general principle, commit to be constructible
    in the same way as their base classes. Calling the return type of this
    function in any way besides passing the five elements, as separate
    arguments, should not be allowed, since that would always be a bug.

    The constructed object, being an (indirect) instance of the tuple class,
    really is a tuple. It satisfies all expectations for tuples, except for its
    customized repr that can be run as code to construct an instance of the
    same (derived) type. It never holds any extra data. Elements are not stored
    redundantly. There are no instance dictionaries, nor slotted attributes.
    (Storing data in a data structure outside the instance is also not done.)

    This is manually implemented. The standard library provides two facilities
    for making named tuple types, both explored below. Neither is used here.

    >>> s = summarize_as_manual_named_tuple([1, 3, 2.5, 3, 4])

    >>> s  # doctest: +NORMALIZE_WHITESPACE
    MyNamedTupleSummary(minimum=1,
                        maximum=4,
                        arithmetic_mean=2.7,
                        geometric_mean=2.45951,
                        harmonic_mean=2.15827)
    >>> isinstance(s, tuple)
    True
    >>> eval(repr(s)) == s
    True

    >>> len({s, summarize_as_manual_named_tuple([1, 3, 3, 2.5, 4]),
    ...      summarize_as_manual_named_tuple([1, 2, 16, 4, 8])})
    2
    >>> s == summarize_as_tuple([1, 3, 2.5, 3, 4])  # Equal to other tuples!
    True

    >>> s[:2]
    (1, 4)
    >>> s * 2
    (1, 4, 2.7, 2.45951, 2.15827, 1, 4, 2.7, 2.45951, 2.15827)

    >>> s.minimum = 1.5
    Traceback (most recent call last):
      ...
    AttributeError: can't set attribute 'minimum'

    >>> _, _, am, _, _ = summarize_as_manual_named_tuple([1, 2, 16, 4, 8])
    >>> am
    6.2

    >>> match summarize_as_manual_named_tuple([1, 2, 16, 4, 8]):
    ...     case MyNamedTupleSummary(geometric_mean=4, harmonic_mean=hm_kwd):
    ...         print(f'Geometric mean four, harmonic mean {hm_kwd}.')
    Geometric mean four, harmonic mean 2.58065.

    >>> match summarize_as_manual_named_tuple([1, 2, 16, 4, 8]):
    ...     case MyNamedTupleSummary(_, _, _, 4, hm_pos):
    ...         print(f'Geometric mean four, harmonic mean {hm_pos}.')
    Geometric mean four, harmonic mean 2.58065.

    >>> match summarize_as_manual_named_tuple([1, 2, 16, 4, 8]):
    ...     case _, _, _, 4, hm:
    ...         print(f'Geometric mean four, harmonic mean {hm}.')
    Geometric mean four, harmonic mean 2.58065.

    >>> all(getattr(MyNamedTupleSummary, name) is getattr(tuple, name)
    ...     for name in ('__eq__', '__hash__', '__iter__', '__getitem__'))
    True
    >>> hasattr(s, '__dict__')  # No instance dictionary.
    False
    >>> class Slotted: __slots__ = ('slot',)
    >>> member_descriptor = type(Slotted.slot)
    >>> any(isinstance(member, member_descriptor)  # And no slotted attributes.
    ...     for member in MyNamedTupleSummary.__dict__.values())
    False
    """
    count = 0
    minimum = math.inf
    maximum = 0
    total = 0
    product = 1
    reciprocals_total = 0

    for value in values:
        if value <= 0:
            raise ValueError(f'nonpositive value {value!r}')

        count += 1
        minimum = min(minimum, value)
        maximum = max(maximum, value)
        total += value
        product *= value
        reciprocals_total += 1 / value

    if count == 0:
        raise ValueError('no values')

    return MyNamedTupleSummary(
        minimum=minimum,
        maximum=maximum,
        arithmetic_mean=round(total / count, precision),
        geometric_mean=round(product**(1 / count), precision),
        harmonic_mean=round(count / reciprocals_total, precision),
    )


# NOTE: One disadvantage of collections.namedtuple is that, if the type is
# renamed by an automated refactoring (at least in current editors/IDEs), the
# typename argument to collections.namedtuple must still be manually changed.
NamedTupleSummary = collections.namedtuple('NamedTupleSummary', (
    'minimum',
    'maximum',
    'arithmetic_mean',
    'geometric_mean',
    'harmonic_mean',
))

NamedTupleSummary.__doc__ = """
    Named tuple summary returned by summarize_as_named_tuple.

    This type is created in the usual way for a named tuple type, using
    collections.namedtuple. It is immutable and iterable, because tuples are.
    """


def summarize_as_named_tuple(values, *, precision=DEFAULT_PRECISION):
    """
    Compute min, max, and arithmetic, geometric, and harmonic mean.

    This is like summarize_as_tuple, but the five computed results are returned
    as an instance of a named tuple class. The class is made using the facility
    in the collections module for doing so. (Such classes often omit docstrings
    because the facility doesn't directly help with them, but they need not be
    omitted. Like all other classes in this module, the class has a docstring.)

    Most named tuple types in Python code are made this way. This satisfies the
    requirements stated in summarize_as_manual_named_tuple. In particular,
    instances of named tuple types, no matter how the types are made, are equal
    to same-length tuples whose corresponding values are equal. This includes
    not just plain tuples, but instances of conceptually unrelated named tuple
    types! Named tuples should only be used when this is reasonable.

    >>> s = summarize_as_named_tuple([1, 3, 2.5, 3, 4])

    >>> s  # doctest: +NORMALIZE_WHITESPACE
    NamedTupleSummary(minimum=1,
                      maximum=4,
                      arithmetic_mean=2.7,
                      geometric_mean=2.45951,
                      harmonic_mean=2.15827)
    >>> isinstance(s, tuple)
    True
    >>> eval(repr(s)) == s
    True

    >>> len({s, summarize_as_named_tuple([1, 3, 3, 2.5, 4]),
    ...      summarize_as_named_tuple([1, 2, 16, 4, 8])})
    2

    >>> from tokenize import TokenInfo  # A highly unrelated named tuple type.
    >>> len({s, summarize_as_tuple([1, 3, 2.5, 3, 4]),
    ...      summarize_as_manual_named_tuple([1, 3, 2.5, 3, 4]),
    ...      TokenInfo(1, 4, 2.7, 2.45951, 2.15827)})
    1

    >>> s[:2]
    (1, 4)
    >>> s * 2
    (1, 4, 2.7, 2.45951, 2.15827, 1, 4, 2.7, 2.45951, 2.15827)

    >>> s.minimum = 1.5  # Subtly different message from MyNamedTupleSummary's.
    Traceback (most recent call last):
      ...
    AttributeError: can't set attribute

    >>> _, _, am, _, _ = summarize_as_named_tuple([1, 2, 16, 4, 8])
    >>> am
    6.2

    >>> match summarize_as_named_tuple([1, 2, 16, 4, 8]):
    ...     case NamedTupleSummary(geometric_mean=4, harmonic_mean=hm_kwd):
    ...         print(f'Geometric mean four, harmonic mean {hm_kwd}.')
    Geometric mean four, harmonic mean 2.58065.

    >>> match summarize_as_named_tuple([1, 2, 16, 4, 8]):
    ...     case NamedTupleSummary(_, _, _, 4, hm_pos):
    ...         print(f'Geometric mean four, harmonic mean {hm_pos}.')
    Geometric mean four, harmonic mean 2.58065.

    >>> match summarize_as_named_tuple([1, 2, 16, 4, 8]):
    ...     case _, _, _, 4, hm:
    ...         print(f'Geometric mean four, harmonic mean {hm}.')
    Geometric mean four, harmonic mean 2.58065.

    >>> all(getattr(NamedTupleSummary, name) is getattr(tuple, name)
    ...     for name in ('__eq__', '__hash__', '__iter__', '__getitem__'))
    True
    >>> hasattr(s, '__dict__')  # No instance dictionary.
    False
    >>> class Slotted: __slots__ = ('slot',)
    >>> member_descriptor = type(Slotted.slot)
    >>> any(isinstance(member, member_descriptor)  # And no slotted attributes.
    ...     for member in NamedTupleSummary.__dict__.values())
    False
    """
    count = 0
    minimum = math.inf
    maximum = 0
    total = 0
    product = 1
    reciprocals_total = 0

    for value in values:
        if value <= 0:
            raise ValueError(f'nonpositive value {value!r}')

        count += 1
        minimum = min(minimum, value)
        maximum = max(maximum, value)
        total += value
        product *= value
        reciprocals_total += 1 / value

    if count == 0:
        raise ValueError('no values')

    return NamedTupleSummary(
        minimum=minimum,
        maximum=maximum,
        arithmetic_mean=round(total / count, precision),
        geometric_mean=round(product**(1 / count), precision),
        harmonic_mean=round(count / reciprocals_total, precision),
    )


class TypedNamedTupleSummary(typing.NamedTuple):
    """
    "Typed" named tuple summary returned by summarized_as_typed_named_tuple and
    summarized_as_typed_named_tuple_typed.

    This type is created using typing.NamedTuple, which is done by specifying
    it as a base class, even though it is not really a base class, and the
    direct base class is tuple (as it is when collections.namedtuple is used).
    This class is immutable and iterable, because tuples are.
    """
    minimum: float
    maximum: float
    arithmetic_mean: float
    geometric_mean: float
    harmonic_mean: float


def summarize_as_typed_named_tuple(values, *, precision=DEFAULT_PRECISION):
    """
    Compute min, max, and arithmetic, geometric, and harmonic mean.

    This is like summarize_as_tuple, but the five computed results are returned
    as an instance of a named tuple class. The class is made using the facility
    in the typing module for doing so. This named tuple type is "typed" in that
    its attributes carry type annotations. These relate to Python's optional
    static typing and do not confer runtime type checking. The interpreter does
    NOT check the annotations. Static type checkers like mypy and pyright do.
    But they won't check this function, which omits parameter and return type
    annotations. This shows "typed" and "untyped" code can be used together.
    The most important thing to know about type annotations, aside from how the
    interpreter doesn't check them, is that code with and without them can mix.

    NOTE: That an instance's attributes have type annotations does not change
    that it is a tuple, supports all operations of tuples, and equals any tuple
    with equal values in the same order, even those of unrelated named tuple
    types. This includes unrelated "typed" named tuple types, even those whose
    attributes' type annotations are totally different. Static type checkers do
    not warn about this, because it is not a type error. If a type's equality
    comparison logic should differ at all from that of tuples, the type should
    not be any kind of named tuple. (This is one reason data classes exist.)

    The facility for named tuples in the typing module can be used in a manner
    similar to the facility in the collections module, but this is rarely done.
    The TypedNameTupleSummary class uses it in the other, much nicer, way.

    >>> s = summarize_as_typed_named_tuple([1, 3, 2.5, 3, 4])

    >>> s  # doctest: +NORMALIZE_WHITESPACE
    TypedNamedTupleSummary(minimum=1,
                           maximum=4,
                           arithmetic_mean=2.7,
                           geometric_mean=2.45951,
                           harmonic_mean=2.15827)
    >>> isinstance(s, tuple)
    True
    >>> eval(repr(s)) == s
    True

    >>> len({s, summarize_as_typed_named_tuple([1, 3, 3, 2.5, 4]),
    ...      summarize_as_typed_named_tuple([1, 2, 16, 4, 8])})
    2

    >>> from tokenize import TokenInfo  # A highly unrelated named tuple type.
    >>> len({s, summarize_as_tuple([1, 3, 2.5, 3, 4]),
    ...      summarize_as_manual_named_tuple([1, 3, 2.5, 3, 4]),
    ...      summarize_as_named_tuple([1, 3, 2.5, 3, 4]),
    ...      TokenInfo(1, 4, 2.7, 2.45951, 2.15827)})
    1

    >>> s[:2]
    (1, 4)
    >>> s * 2
    (1, 4, 2.7, 2.45951, 2.15827, 1, 4, 2.7, 2.45951, 2.15827)

    >>> s.minimum = 1.5  # Subtly different message from MyNamedTupleSummary's.
    Traceback (most recent call last):
      ...
    AttributeError: can't set attribute

    >>> _, _, am, _, _ = summarize_as_typed_named_tuple([1, 2, 16, 4, 8])
    >>> am
    6.2

    >>> match summarize_as_typed_named_tuple([1, 2, 16, 4, 8]):
    ...     case TypedNamedTupleSummary(geometric_mean=4,
    ...                                 harmonic_mean=hm_kwd):
    ...         print(f'Geometric mean four, harmonic mean {hm_kwd}.')
    Geometric mean four, harmonic mean 2.58065.

    >>> match summarize_as_typed_named_tuple([1, 2, 16, 4, 8]):
    ...     case TypedNamedTupleSummary(_, _, _, 4, hm_pos):
    ...         print(f'Geometric mean four, harmonic mean {hm_pos}.')
    Geometric mean four, harmonic mean 2.58065.

    >>> match summarize_as_typed_named_tuple([1, 2, 16, 4, 8]):
    ...     case _, _, _, 4, hm:
    ...         print(f'Geometric mean four, harmonic mean {hm}.')
    Geometric mean four, harmonic mean 2.58065.

    >>> all(getattr(TypedNamedTupleSummary, name) is getattr(tuple, name)
    ...     for name in ('__eq__', '__hash__', '__iter__', '__getitem__'))
    True
    >>> hasattr(s, '__dict__')  # No instance dictionary.
    False
    >>> class Slotted: __slots__ = ('slot',)
    >>> member_descriptor = type(Slotted.slot)
    >>> any(isinstance(member, member_descriptor)  # And no slotted attributes.
    ...     for member in TypedNamedTupleSummary.__dict__.values())
    False
    """
    count = 0
    minimum = math.inf
    maximum = 0
    total = 0
    product = 1
    reciprocals_total = 0

    for value in values:
        if value <= 0:
            raise ValueError(f'nonpositive value {value!r}')

        count += 1
        minimum = min(minimum, value)
        maximum = max(maximum, value)
        total += value
        product *= value
        reciprocals_total += 1 / value

    if count == 0:
        raise ValueError('no values')

    return TypedNamedTupleSummary(
        minimum=minimum,
        maximum=maximum,
        arithmetic_mean=round(total / count, precision),
        geometric_mean=round(product**(1 / count), precision),
        harmonic_mean=round(count / reciprocals_total, precision),
    )


def summarize_as_typed_named_tuple_typed(
        values: Iterable[float], *,
        precision: int = DEFAULT_PRECISION) -> TypedNamedTupleSummary:
    """
    Compute min, max, and arithmetic, geometric, and harmonic mean.

    This is the same as summarize_as_typed_named_tuple above, but this function
    has parameter and return type annotations, for static type checking. Both
    functions are included, to emphasize that type annotations in a function or
    class don't force callers to use them. (But subsequent functions in this
    module, if their return types' attributes have type annotations, have them
    too. This avoids a level of repetition excessive even for this module.)

    NOTE: Type checkers unfortunately do not (currently) check doctests. Also,
    like other class and function names in this module, this function is named
    verbosely to make it easy to distinguish from others. This module shows
    numerous ways to achieve a similar effect. If not for that, we would write
    one "Summary" class and one "summarize" function, with those short names.

    [FIXME: Add the type annotations on this function's parameters and return
    type. Then run mypy on this module. If there are any problems, make sure
    you understand them, then fix them in a suitable way.]

    >>> s = summarize_as_typed_named_tuple_typed([1, 3, 2.5, 3, 4])

    >>> s  # doctest: +NORMALIZE_WHITESPACE
    TypedNamedTupleSummary(minimum=1,
                           maximum=4,
                           arithmetic_mean=2.7,
                           geometric_mean=2.45951,
                           harmonic_mean=2.15827)
    >>> isinstance(s, tuple)
    True
    >>> eval(repr(s)) == s
    True

    >>> len({s, summarize_as_typed_named_tuple_typed([1, 3, 3, 2.5, 4]),
    ...      summarize_as_typed_named_tuple_typed([1, 2, 16, 4, 8])})
    2

    >>> from tokenize import TokenInfo  # A highly unrelated named tuple type.
    >>> len({s, summarize_as_tuple([1, 3, 2.5, 3, 4]),
    ...      summarize_as_manual_named_tuple([1, 3, 2.5, 3, 4]),
    ...      summarize_as_named_tuple([1, 3, 2.5, 3, 4]),
    ...      TokenInfo(1, 4, 2.7, 2.45951, 2.15827)})
    1

    >>> s[:2]
    (1, 4)
    >>> s * 2
    (1, 4, 2.7, 2.45951, 2.15827, 1, 4, 2.7, 2.45951, 2.15827)

    >>> s.minimum = 1.5  # Subtly different message from MyNamedTupleSummary's.
    Traceback (most recent call last):
      ...
    AttributeError: can't set attribute

    >>> _, _, am, _, _ = summarize_as_typed_named_tuple_typed([1, 2, 16, 4, 8])
    >>> am
    6.2

    >>> match summarize_as_typed_named_tuple_typed([1, 2, 16, 4, 8]):
    ...     case TypedNamedTupleSummary(geometric_mean=4,
    ...                                 harmonic_mean=hm_kwd):
    ...         print(f'Geometric mean four, harmonic mean {hm_kwd}.')
    Geometric mean four, harmonic mean 2.58065.

    >>> match summarize_as_typed_named_tuple_typed([1, 2, 16, 4, 8]):
    ...     case TypedNamedTupleSummary(_, _, _, 4, hm_pos):
    ...         print(f'Geometric mean four, harmonic mean {hm_pos}.')
    Geometric mean four, harmonic mean 2.58065.

    >>> match summarize_as_typed_named_tuple_typed([1, 2, 16, 4, 8]):
    ...     case _, _, _, 4, hm:
    ...         print(f'Geometric mean four, harmonic mean {hm}.')
    Geometric mean four, harmonic mean 2.58065.
    """
    count = 0
    minimum = math.inf
    maximum = 0.0
    total = 0.0
    product = 1.0
    reciprocals_total = 0.0

    for value in values:
        if value <= 0:
            raise ValueError(f'nonpositive value {value!r}')

        count += 1
        minimum = min(minimum, value)
        maximum = max(maximum, value)
        total += value
        product *= value
        reciprocals_total += 1 / value

    if count == 0:
        raise ValueError('no values')

    return TypedNamedTupleSummary(
        minimum=minimum,
        maximum=maximum,
        arithmetic_mean=round(total / count, precision),
        geometric_mean=round(product**(1 / count), precision),
        harmonic_mean=round(count / reciprocals_total, precision),
    )


@attrs.frozen  # Or: @attrs.define(frozen=True)
class FrozenSummary:
    """Immutable summary returned by summarize_as_frozen_attrs."""

    minimum = attrs.field()
    maximum = attrs.field()
    arithmetic_mean = attrs.field()
    geometric_mean = attrs.field()
    harmonic_mean = attrs.field()


def summarize_as_frozen_attrs(values, *, precision=DEFAULT_PRECISION):
    """
    Compute min, max, and arithmetic, geometric, and harmonic mean.

    This is like summarize_as_tuple, but the five computed results are returned
    as an instance of an immutable data class, made with attrs, using the
    modern API. Neither that class nor this function use type annotations.

    >>> s = summarize_as_frozen_attrs([1, 3, 2.5, 3, 4])

    >>> s  # doctest: +NORMALIZE_WHITESPACE
    FrozenSummary(minimum=1,
                  maximum=4,
                  arithmetic_mean=2.7,
                  geometric_mean=2.45951,
                  harmonic_mean=2.15827)

    >>> len({s, summarize_as_frozen_attrs([1, 3, 3, 2.5, 4]),
    ...      summarize_as_frozen_attrs([1, 2, 16, 4, 8])})
    2

    >>> s.minimum = 1.5  # No message, but the exception type is very specific.
    Traceback (most recent call last):
      ...
    attr.exceptions.FrozenInstanceError
    >>> try:
    ...     s.minimum = 1.5
    ... except AttributeError:
    ...     print('FrozenInstanceError is a subclass of AttributeError.')
    FrozenInstanceError is a subclass of AttributeError.

    >>> _, _, am, _, _ = summarize_as_frozen_attrs([1, 2, 16, 4, 8])
    Traceback (most recent call last):
      ...
    TypeError: cannot unpack non-iterable FrozenSummary object

    >>> match summarize_as_frozen_attrs([1, 2, 16, 4, 8]):
    ...     case FrozenSummary(geometric_mean=4, harmonic_mean=hm_kwd):
    ...         print(f'Geometric mean four, harmonic mean {hm_kwd}.')
    Geometric mean four, harmonic mean 2.58065.

    >>> match summarize_as_frozen_attrs([1, 2, 16, 4, 8]):
    ...     case FrozenSummary(_, _, _, 4, hm_pos):
    ...         print(f'Geometric mean four, harmonic mean {hm_pos}.')
    Geometric mean four, harmonic mean 2.58065.
    """
    count = 0
    minimum = math.inf
    maximum = 0
    total = 0
    product = 1
    reciprocals_total = 0

    for value in values:
        if value <= 0:
            raise ValueError(f'nonpositive value {value!r}')

        count += 1
        minimum = min(minimum, value)
        maximum = max(maximum, value)
        total += value
        product *= value
        reciprocals_total += 1 / value

    if count == 0:
        raise ValueError('no values')

    return FrozenSummary(
        minimum=minimum,
        maximum=maximum,
        arithmetic_mean=round(total / count, precision),
        geometric_mean=round(product**(1 / count), precision),
        harmonic_mean=round(count / reciprocals_total, precision),
    )


@attrs.frozen  # Or: @attrs.define(frozen=True)
class TypedFrozenSummary:
    """
    "Typed" immutable summary returned by summarize_as_typed_frozen_attrs.
    """

    minimum: float
    maximum: float
    arithmetic_mean: float
    geometric_mean: float
    harmonic_mean: float


def summarize_as_typed_frozen_attrs(
        values: Iterable[float], *,
        precision: int = DEFAULT_PRECISION) -> TypedFrozenSummary:
    """
    Compute min, max, and arithmetic, geometric, and harmonic mean.

    This is like summarize_as_tuple, but the five computed results are returned
    as an instance of an immutable data class, made with attrs, using the
    modern API. Both that class and this function use type annotations.

    [FIXME: Run mypy on this module. Fix any problems.]

    >>> s = summarize_as_typed_frozen_attrs([1, 3, 2.5, 3, 4])

    >>> s  # doctest: +NORMALIZE_WHITESPACE
    TypedFrozenSummary(minimum=1,
                       maximum=4,
                       arithmetic_mean=2.7,
                       geometric_mean=2.45951,
                       harmonic_mean=2.15827)

    >>> len({s, summarize_as_typed_frozen_attrs([1, 3, 3, 2.5, 4]),
    ...      summarize_as_typed_frozen_attrs([1, 2, 16, 4, 8])})
    2

    >>> s.minimum = 1.5  # No message, but the exception type is very specific.
    Traceback (most recent call last):
      ...
    attr.exceptions.FrozenInstanceError
    >>> try:
    ...     s.minimum = 1.5
    ... except AttributeError:
    ...     print('FrozenInstanceError is a subclass of AttributeError.')
    FrozenInstanceError is a subclass of AttributeError.

    >>> _, _, am, _, _ = summarize_as_typed_frozen_attrs([1, 2, 16, 4, 8])
    Traceback (most recent call last):
      ...
    TypeError: cannot unpack non-iterable TypedFrozenSummary object

    >>> match summarize_as_typed_frozen_attrs([1, 2, 16, 4, 8]):
    ...     case TypedFrozenSummary(geometric_mean=4, harmonic_mean=hm_kwd):
    ...         print(f'Geometric mean four, harmonic mean {hm_kwd}.')
    Geometric mean four, harmonic mean 2.58065.

    >>> match summarize_as_typed_frozen_attrs([1, 2, 16, 4, 8]):
    ...     case TypedFrozenSummary(_, _, _, 4, hm_pos):
    ...         print(f'Geometric mean four, harmonic mean {hm_pos}.')
    Geometric mean four, harmonic mean 2.58065.
    """
    count = 0
    minimum = math.inf
    maximum = 0.0
    total = 0.0
    product = 1.0
    reciprocals_total = 0.0

    for value in values:
        if value <= 0:
            raise ValueError(f'nonpositive value {value!r}')

        count += 1
        minimum = min(minimum, value)
        maximum = max(maximum, value)
        total += value
        product *= value
        reciprocals_total += 1 / value

    if count == 0:
        raise ValueError('no values')

    return TypedFrozenSummary(
        minimum=minimum,
        maximum=maximum,
        arithmetic_mean=round(total / count, precision),
        geometric_mean=round(product**(1 / count), precision),
        harmonic_mean=round(count / reciprocals_total, precision),
    )


@attrs.mutable  # Or: @attrs.define  Or: @attrs.define(frozen=False)
class MutableSummary:
    """Mutable summary returned by summarize_as_frozen_attrs."""

    minimum = attrs.field()
    maximum = attrs.field()
    arithmetic_mean = attrs.field()
    geometric_mean = attrs.field()
    harmonic_mean = attrs.field()


def summarize_as_mutable_attrs(values, *, precision=DEFAULT_PRECISION):
    """
    Compute min, max, and arithmetic, geometric, and harmonic mean.

    This is like summarize_as_tuple, but the five computed results are returned
    as an instance of a mutable data class, made with attrs, using the modern
    API. Neither that class nor this function use type annotations.

    >>> s = summarize_as_mutable_attrs([1, 3, 2.5, 3, 4])

    >>> s  # doctest: +NORMALIZE_WHITESPACE
    MutableSummary(minimum=1,
                   maximum=4,
                   arithmetic_mean=2.7,
                   geometric_mean=2.45951,
                   harmonic_mean=2.15827)

    >>> hash(s)
    Traceback (most recent call last):
      ...
    TypeError: unhashable type: 'MutableSummary'

    >>> s == summarize_as_mutable_attrs([1, 3, 3, 2.5, 4])
    True
    >>> s == summarize_as_mutable_attrs([1, 2, 16, 4, 8])
    False
    >>> s.minimum = 1.5; s == summarize_as_mutable_attrs([1, 3, 2.5, 3, 4])
    False

    >>> _, _, am, _, _ = summarize_as_mutable_attrs([1, 2, 16, 4, 8])
    Traceback (most recent call last):
      ...
    TypeError: cannot unpack non-iterable MutableSummary object

    >>> match summarize_as_mutable_attrs([1, 2, 16, 4, 8]):
    ...     case MutableSummary(geometric_mean=4, harmonic_mean=hm_kwd):
    ...         print(f'Geometric mean four, harmonic mean {hm_kwd}.')
    Geometric mean four, harmonic mean 2.58065.

    >>> match summarize_as_mutable_attrs([1, 2, 16, 4, 8]):
    ...     case MutableSummary(_, _, _, 4, hm_pos):
    ...         print(f'Geometric mean four, harmonic mean {hm_pos}.')
    Geometric mean four, harmonic mean 2.58065.
    """
    count = 0
    minimum = math.inf
    maximum = 0
    total = 0
    product = 1
    reciprocals_total = 0

    for value in values:
        if value <= 0:
            raise ValueError(f'nonpositive value {value!r}')

        count += 1
        minimum = min(minimum, value)
        maximum = max(maximum, value)
        total += value
        product *= value
        reciprocals_total += 1 / value

    if count == 0:
        raise ValueError('no values')

    return MutableSummary(
        minimum=minimum,
        maximum=maximum,
        arithmetic_mean=round(total / count, precision),
        geometric_mean=round(product**(1 / count), precision),
        harmonic_mean=round(count / reciprocals_total, precision),
    )


@attrs.mutable   # Or: @attrs.define  Or: @attrs.define(frozen=False)
class TypedMutableSummary:
    """"Typed" mutable summary returned by summarize_as_typed_mutable_attrs."""

    minimum: float
    maximum: float
    arithmetic_mean: float
    geometric_mean: float
    harmonic_mean: float


def summarize_as_typed_mutable_attrs(
        values: Iterable[float], *,
        precision: int = DEFAULT_PRECISION) -> TypedMutableSummary:
    """
    Compute min, max, and arithmetic, geometric, and harmonic mean.

    This is like summarize_as_tuple, but the five computed results are returned
    as an instance of a mutable data class, made with attrs, using the modern
    API. Both that class and this function use type annotations.

    [FIXME: Run mypy on this module. Fix any problems.]

    >>> s = summarize_as_typed_mutable_attrs([1, 3, 2.5, 3, 4])

    >>> s  # doctest: +NORMALIZE_WHITESPACE
    TypedMutableSummary(minimum=1,
                        maximum=4,
                        arithmetic_mean=2.7,
                        geometric_mean=2.45951,
                        harmonic_mean=2.15827)

    >>> hash(s)
    Traceback (most recent call last):
      ...
    TypeError: unhashable type: 'TypedMutableSummary'

    >>> s == summarize_as_typed_mutable_attrs([1, 3, 3, 2.5, 4])
    True
    >>> s == summarize_as_typed_mutable_attrs([1, 2, 16, 4, 8])
    False
    >>> s.minimum = 1.5
    >>> s == summarize_as_typed_mutable_attrs([1, 3, 2.5, 3, 4])
    False

    >>> _, _, am, _, _ = summarize_as_typed_mutable_attrs([1, 2, 16, 4, 8])
    Traceback (most recent call last):
      ...
    TypeError: cannot unpack non-iterable TypedMutableSummary object

    >>> match summarize_as_typed_mutable_attrs([1, 2, 16, 4, 8]):
    ...     case TypedMutableSummary(geometric_mean=4, harmonic_mean=hm_kwd):
    ...         print(f'Geometric mean four, harmonic mean {hm_kwd}.')
    Geometric mean four, harmonic mean 2.58065.

    >>> match summarize_as_typed_mutable_attrs([1, 2, 16, 4, 8]):
    ...     case TypedMutableSummary(_, _, _, 4, hm_pos):
    ...         print(f'Geometric mean four, harmonic mean {hm_pos}.')
    Geometric mean four, harmonic mean 2.58065.
    """
    count = 0
    minimum = math.inf
    maximum = 0.0
    total = 0.0
    product = 1.0
    reciprocals_total = 0.0

    for value in values:
        if value <= 0:
            raise ValueError(f'nonpositive value {value!r}')

        count += 1
        minimum = min(minimum, value)
        maximum = max(maximum, value)
        total += value
        product *= value
        reciprocals_total += 1 / value

    if count == 0:
        raise ValueError('no values')

    return TypedMutableSummary(
        minimum=minimum,
        maximum=maximum,
        arithmetic_mean=round(total / count, precision),
        geometric_mean=round(product**(1 / count), precision),
        harmonic_mean=round(count / reciprocals_total, precision),
    )


def summarize_as_tuple_alt(values, *, precision=DEFAULT_PRECISION):
    """
    Compute min, max, and arithmetic, geometric, and harmonic mean.

    This alternative implementation of summarize_as_tuple is very short, making
    use of summarize_as_frozen_attrs and something in the attrs module. No
    other functions or classes are introduced for support. This calls
    summarize_as_frozen_attrs but makes no direct or indirect use of any other
    function in this module. This makes indirect use of FrozenSummary
    (summarize_as_frozen_attrs returns an instance of it) but does not call it.

    The purpose of this function is to show how it is quick and simple to get a
    tuple from an attrs data class instance. This doesn't depend on whether the
    attrs class is mutable, nor on whether it has type hints. (It also does not
    depend on whether it was defined with the attrs library's modern API, or
    its classic API, shown below.) Replacing summarize_as_frozen_attrs with a
    call to any of the other functions in this module that return a "summary"
    as an instance of an attrs data class would produce the same result.

    >>> summarize_as_tuple_alt([1, 3, 2.5, 3, 4])
    (1, 4, 2.7, 2.45951, 2.15827)
    >>> type(_)
    <class 'tuple'>

    >>> len({summarize_as_tuple_alt([1, 3, 2.5, 3, 4]),
    ...      summarize_as_tuple_alt([1, 3, 3, 2.5, 4]),
    ...      summarize_as_tuple_alt([1, 2, 16, 4, 8])})
    2

    >>> _, _, am, _, _ = summarize_as_tuple_alt([1, 2, 16, 4, 8])
    >>> am
    6.2

    >>> match summarize_as_tuple_alt([1, 2, 16, 4, 8]):
    ...     case _, _, _, 4, hm:
    ...         print(f'Geometric mean four, harmonic mean {hm}.')
    Geometric mean four, harmonic mean 2.58065.

    >>> summarize_as_tuple_alt([1, 3, 2.5, 3, 4], precision=4)
    (1, 4, 2.7, 2.4595, 2.1583)
    """
    summary = summarize_as_frozen_attrs(values, precision=precision)
    return attrs.astuple(summary)


def summarize_as_dict_alt(values, *, precision=DEFAULT_PRECISION):
    """
    Compute min, max, and arithmetic, geometric, and harmonic mean.

    This is like summarize_as_dict, except (a) keys contain underscores instead
    of spaces, and (b) this is very short, using summarize_as_frozen_attrs and
    something in the attrs module. This is similar to summarize_as_tuple_alt,
    but for dict instead of tuple. The technique likewise works for all attrs
    classes. It does not depend on whether instance dictionaries are present.
    (attrs classes defined with the modern API use __slots__ by default.)

    >>> s = summarize_as_dict_alt([1, 3, 2.5, 3, 4])

    >>> s  # doctest: +NORMALIZE_WHITESPACE
    {'minimum': 1,
     'maximum': 4,
     'arithmetic_mean': 2.7,
     'geometric_mean': 2.45951,
     'harmonic_mean': 2.15827}

    >>> hash(s)
    Traceback (most recent call last):
      ...
    TypeError: unhashable type: 'dict'

    >>> s == summarize_as_dict_alt([1, 3, 3, 2.5, 4])
    True
    >>> s == summarize_as_dict_alt([1, 2, 16, 4, 8])
    False

    >>> match summarize_as_dict_alt([1, 2, 16, 4, 8]):
    ...     case {'geometric_mean': 4, 'harmonic_mean': hm}:
    ...         print(f'Geometric mean four, harmonic mean {hm}.')
    Geometric mean four, harmonic mean 2.58065.

    >>> summarize_as_dict_alt([1, 3, 2.5, 3, 4], precision=4)['harmonic_mean']
    2.1583

    The reason this stipulates different key is that summarize_as_dict shows
    show how a dictionary can be used to return aggregate results and that one
    need not limit oneself to valid identifiers when doing so, while this shows
    how to get a dict from a data class instance. If needed, you could do:

    >>> spaced = {name.replace('_', ' '): value for name, value in s.items()}
    >>> spaced == summarize_as_dict([1, 3, 2.5, 3, 4])
    True
    """
    summary = summarize_as_frozen_attrs(values, precision=precision)
    return attrs.asdict(summary)


__all__ = [thing.__name__ for thing in (  # type: ignore[attr-defined]
    summarize_as_tuple,
    summarize_as_dict,
    summarize_as_simple_namespace,
    MyMutableSummary,
    summarize_as_mutable,
    MyMutableSummaryUnpack,
    summarize_as_mutable_unpack,
    MyFrozenSummary,
    summarize_as_frozen,
    MyFrozenSummaryUnpack,
    summarize_as_frozen_unpack,
    MyNamedTupleSummary,
    summarize_as_manual_named_tuple,
    NamedTupleSummary,
    summarize_as_named_tuple,
    TypedNamedTupleSummary,
    summarize_as_typed_named_tuple,
    summarize_as_typed_named_tuple_typed,
    FrozenSummary,
    summarize_as_frozen_attrs,
    TypedFrozenSummary,
    summarize_as_typed_frozen_attrs,
    MutableSummary,
    summarize_as_mutable_attrs,
    TypedMutableSummary,
    summarize_as_typed_mutable_attrs,
    summarize_as_tuple_alt,
    summarize_as_dict_alt,
)]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
