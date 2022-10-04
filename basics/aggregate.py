#!/usr/bin/env python3

"""
Named tuples and data classes.

This module starts with manual approaches to a problem of data aggregation that
is straightforward, yet (1) an imperfect fit for preexisting built-in and other
standard library types and (2) cumbersome to solve from scratch with explicitly
written special (dunder) methods. Named tuples and data classes solve it well.

Because the attrs library fully supports being used both with and without type
annotations and is extremely popular, a major focus here is on using that
library to make data classes. However, the dataclasses module is shown too.

A goal of this module is to show alternatives, so code is freely duplicated
across functions, and across classes, when sharing it would obscure anything or
make any alternative less self contained -- except where noted otherwise.
"""

import math
import types

DEFAULT_PRECISION = 5
"""How many fractional digits summarize* functions keep when rounding means."""


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
    Manually named tuple summary returned by summarize_as_manual_named_tuple.

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
    as an instance of a custom class that inherits from tuple, extending its
    functionality to allow the elements to be accessed as named attributes. For
    example, if summary is returned, summary.harmonic_mean accesses the same
    element summary[4] and summary[-1] access. Subscripting is still permitted.

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


__all__ = [thing.__name__ for thing in (
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
)]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
