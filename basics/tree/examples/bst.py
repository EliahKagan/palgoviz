"""Nontrivial but mostly small examples of binary search trees (BSTs)."""


def left_only(t):
    """Make a BST with a root and left child."""
    return t(2, t(1), None)


def right_only(t):
    """Make a BST with a root and right child."""
    return t(1, None, t(2))


def tiny(t):
    """Make a 3-node BST of minimal height."""
    return t(2, t(1), t(3))


def small(t):
    """Make a 7-node BST of minimal height."""
    return t(4, t(2, t(1), t(3)), t(6, t(5), t(7)))

def small_str(t):
    """Make a 7-node BST of minimal height whose elements are strings."""
    # The noqa is for "continuation line over-indented for visual indent".
    return t('salamander', t('lizard', t('iguana'), t('newt')),
                           t('tortoise', t('snake'), t('turtle')))

def small_no_left_left(t):
    """Make a 6-node balanced BST with the 1st bottom-level position empty."""
    return t(4, t(2, None, t(3)), t(6, t(5), t(7)))


def small_no_left_right(t):
    """Make a 6-node balanced BST with the 2nd bottom-level position empty."""
    return t(4, t(2, t(1), None), t(6, t(5), t(7)))


def small_no_right_left(t):
    """Make a 6-node balanced BST with the 3rd bottom-level position empty."""
    return t(4, t(2, t(1), t(3)), t(6, None, t(7)))


def small_no_right_right(t):
    """Make a 6-node balanced BST with the 4th bottom-level position empty."""
    return t(4, t(2, t(1), t(3)), t(6, t(5), None))


def left_chain(t):
    """Make a 5-node BST in which no node has a right child."""
    return t(5, t(4, t(3, t(2, t(1), None), None), None), None)


def right_chain(t):
    """Make a 5-node BST in which no node has a left child."""
    return t(1, None, t(2, None, t(3, None, t(4, None, t(5)))))


def zigzag_chain(t):
    """Make a 5-node BST of maximum depth, alternating left and right."""
    return t(1, None, t(5, t(2, None, t(4, t(3), None)), None))


def lefty(t):
    """Make a 9-node BST whose right branches never have multiple nodes."""
    return t(8, t(6, t(4, t(2, t(1), t(3)), t(5)), t(7)), t(9))


def righty(t):
    """Make a 9-node BST whose left branches never have multiple nodes."""
    return t(2, t(1), t(4, t(3), t(6, t(5), t(8, t(7), t(9)))))


def medium(t):
    """Make a mostly balanced 24-node BST with a few duplicate elements."""
    # The noqa are for "continuation line over-indented for visual indent".
    return t(11, t(4,  t(2,  t(1, t(1), t(2)),
                             t(3, None, t(3))),     # noqa: E127
                       t(8,  t(6, t(5), t(7)),      # noqa: E127
                             t(10, t(9), None))),   # noqa: E127
                 t(15, t(13, t(12), t(14)),         # noqa: E127
                       t(19, t(17, t(16), t(18)),   # noqa: E127
                             t(20, None, t(21)))))  # noqa: E127
