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

"""Small examples of binary trees that have left-right (bilateral) symmetry."""

from . import basic as _basic
from . import mirror as _mirror


def tiny(t):
    """Make a 3-node bilateral tree of minimal height."""
    return t(1, t(2), t(2))


def small(t):
    """Make a 7-node bilateral tree of minimal height."""
    return t(7, t(9, t(4), t(5)), t(9, t(5), t(4)))


def small_no_corners(t):
    """Make a 5-node bilateral tree with no left-left and right-right nodes."""
    return t(7, t(9, None, t(5)), t(9, t(5), None))


def small_no_center(t):
    """Make a 5-node bilateral tree with no left-right and right-left nodes."""
    return t(7, t(9, t(4), None), t(9, None, t(4)))


def medium_large(t):
    """Make a mostly balanced 49-node bilateral tree."""
    return t(0, _basic.medium(t), _mirror.medium(t))


def medium_large_redundant(t):
    """Make a mostly balanced 49-node bilateral tree with extra duplication."""
    return t(0, _basic.medium_redundant(t), _mirror.medium_redundant(t))
