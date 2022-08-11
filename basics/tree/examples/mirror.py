"""
Left-right mirror images ("reflections") of the tree.examples.basic examples.

These are named correspondingly, even when the names do not, by themselves,
accurately describe the trees these factories make. Possible confusion arising
from this can be avoided by accessing these with the module name, such as by
importing reflected from tree.examples and saying reflected.small_no_left_left,
rather than by importing small_no_left_left from tree.examples.reflected.
"""


def left_only(t):
    """Make a tree whose reflection has a root and left child."""
    return t(1, None, t(2))


def right_only(t):
    """Make a tree whose reflection has a root and right child."""
    return t(2, t(1), None)


def tiny(t):
    """Make a 3-node tree of minimal height."""
    return t(1, t(3), t(2))


def small(t):
    """Make a 7-node tree of minimal height."""
    return t(1, t(3, t(7), t(6)), t(2, t(5), t(4)))


def small_str(t):
    """Make a 7-node tree of minimal height whose elements are strings."""
    # The noqa is for "continuation line over-indented for visual indent".
    return t('iguana', t('newt', t('turtle'), t('tortoise')),
                       t('lizard', t('snake'), t('salamander')))  # noqa: E127


def small_no_left_left(t):
    """
    Make a 6-node balanced tree whose reflection has the 1st bottom-level
    position empty.
    """
    return t(1, t(3, t(6), t(5)), t(2, t(4), None))


def small_no_left_right(t):
    """
    Make a 6-node balanced tree whose reflection has the 2nd bottom-level
    position empty.
    """
    return t(1, t(3, t(6), t(5)), t(2, None, t(4)))


def small_no_right_left(t):
    """
    Make a 6-node balanced tree whose reflection has the 3rd bottom-level
    position empty.
    """
    return t(1, t(3, t(6), None), t(2, t(5), t(4)))


def small_no_right_right(t):
    """
    Make a 6-node balanced tree whose reflection has the 4th bottom-level
    position empty.
    """
    return t(1, t(3, None, t(6)), t(2, t(5), t(4)))


def left_chain(t):
    """Make a 5-node tree whose reflection has no nodes with right children."""
    return t(1, None, t(2, None, t(3, None, t(4, None, t(5)))))


def right_chain(t):
    """Make a 5-node tree whose reflection has no nodes with left children."""
    return t(5, t(4, t(3, t(2, t(1), None), None), None), None)


def zigzag_chain(t):
    """Make a 5-node tree of maximum depth, alternating left and right."""
    return t(1, t(2, None, t(3, t(4, None, t(5)), None)), None)


def lefty(t):
    """Make a 9-node tree whose reflection has single-node right branches."""
    return t(1, t(3), t(2, t(5), t(4, t(7), t(6, t(9), t(8)))))


def righty(t):
    """Make a 9-node tree whose reflection has single-node left-branches."""
    return t(1, t(3, t(5, t(7, t(9), t(8)), t(6)), t(4)), t(2))


def medium(t):
    """Make a mostly balanced 24-node tree with a few duplicate elements."""
    # The noqa are for "continuation line over-indented for visual indent".
    return t(1, t(3, t(7, t(15, t(3), None),
                          t(14, t(2), t(1))),    # noqa: E127
                     t(6, t(13), t(12))),        # noqa: E127
                t(2, t(5, t(11, None, t(21)),    # noqa: E127
                          t(10, t(20), t(19))),  # noqa: E127
                     t(4, t(9, t(18), None),     # noqa: E127
                          t(8, t(17), t(16)))))  # noqa: E127


def medium_redundant(t):
    """Make a mostly balanced 24-node tree with lots of subtree duplication."""
    # The noqa are for "continuation line over-indented for visual indent".
    return t(1, t(3, t(7, t(15, t(3), None),
                          t(14, t(2), t(1))),   # noqa: E127
                     t(6, t(13), t(12))),       # noqa: E127
                t(2, t(5, t(11, None, t(21)),   # noqa: E127
                          t(6, t(13), t(12))),  # noqa: E127
                     t(7, t(15, t(3), None),    # noqa: E127
                          t(14, t(2), t(1)))))  # noqa: E127
