"""Small examples of binary trees that have left-right (bilateral) symmetry."""

import itertools as _itertools

from . import basic as _basic, mirror as _mirror


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
