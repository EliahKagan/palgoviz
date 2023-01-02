"""Examples of trivial cases of binary trees."""


def empty(_t):
    """Make a "tree" with no nodes."""
    return None


def singleton(t):
    """Make a tree with only one node."""
    return t(1)
