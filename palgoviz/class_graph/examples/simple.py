# Copyright (c) 2022 Eliah Kagan
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

"""Simple examples of class hierarchies."""

from palgoviz import testing as _testing


class A(metaclass=_testing.ShortReprMeta):
    """Top class in an inheritance diamond, for testing."""


class B(A):
    """Left class in an inheritance diamond, for testing."""


class C(A):
    """Right class in an inheritance diamond, for testing."""


class D(B, C):
    """Bottom class in an inheritance diamond, for testing."""


def not_object(cls):
    """Filter to omit the object from traversal, for cleaner output."""
    return cls is not object
