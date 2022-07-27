"""Nontrivial but mostly small examples of non-BST binary trees."""


def left_only(t):
    """Make a tree with a root and left child."""
    return t(1, t(2), None)


def right_only(t):
    """Make a tree with a root and right child."""
    return t(2, None, t(1))  # Deliberately not a BST. See tree.examples.bst.


def tiny(t):
    """Make a 3-node tree of minimal height."""
    return t(1, t(2), t(3))


def small(t):
    """Make a 7-node tree of minimal height."""
    return t(1, t(2, t(4), t(5)), t(3, t(6), t(7)))


def small_no_left_left(t):
    """Make a 6-node balanced tree with the 1st bottom-level position empty."""
    return t(1, t(2, None, t(4)), t(3, t(5), t(6)))


def small_no_left_right(t):
    """Make a 6-node balanced tree with the 2nd bottom-level position empty."""
    return t(1, t(2, t(4), None), t(3, t(5), t(6)))


def small_no_right_left(t):
    """Make a 6-node balanced tree with the 3rd bottom-level position empty."""
    return t(1, t(2, t(4), t(5)), t(3, None, t(6)))


def small_no_right_right(t):
    """Make a 6-node balanced tree with the 4th bottom-level position empty."""
    return t(1, t(2, t(4), t(5)), t(3, t(6), None))


def left_chain(t):
    """Make a 5-node tree in which no node has a right child."""
    return t(1, t(2, t(3, t(4, t(5), None), None), None), None)


def right_chain(t):
    """Make a 5-node tree in which no node has a left child."""
    # Deliberately not a BST. See tree.examples.bst.
    return t(5, None, t(4, None, t(3, None, t(2, None, t(1)))))


def zigzag_chain(t):
    """Make a 5-node tree of maximum depth, alternating left and right."""
    return t(1, None, t(2, t(3, None, t(4, t(5), None)), None))


def lefty(t):
    """Make a 9-node tree whose right branches never have multiple nodes."""
    return t(1, t(2, t(4, t(6, t(8), t(9)), t(7)), t(5)), t(3))


def righty(t):
    """Make a 9-node tree whose left branches never have multiple nodes."""
    return t(1, t(2), t(3, t(4), t(5, t(6), t(7, t(8), t(9)))))


def medium(t):
    """Make a mostly balanced 24-node tree with a few duplicate elements."""
    # The noqa are for "continuation line over-indented for visual indent".
    return t(1, t(2, t(4, t(8, t(16), t(17)),
                          t(9, None, t(18))),    # noqa: E127
                     t(5, t(10, t(19), t(20)),   # noqa: E127
                          t(11, t(21), None))),  # noqa: E127
                t(3, t(6, t(12), t(13)),         # noqa: E127
                     t(7, t(14, t(1), t(2)),     # noqa: E127
                          t(15, None, t(3)))))   # noqa: E127


def medium_redundant(t):
    """Make a mostly balanced 24-node tree with lots of subtree duplication."""
    # The noqa are for "continuation line over-indented for visual indent".
    return t(1, t(2, t(7, t(14, t(1), t(2)),
                          t(15, None, t(3))),    # noqa: E127
                     t(5, t(6, t(12), t(13)),    # noqa: E127
                          t(11, t(21), None))),  # noqa: E127
                t(3, t(6, t(12), t(13)),         # noqa: E127
                     t(7, t(14, t(1), t(2)),     # noqa: E127
                          t(15, None, t(3)))))   # noqa: E127
