"""Examples of trivial cases of binary trees."""


def empty(_t):
    """A "tree" with no nodes."""
    return None


def singleton(t):
    """A tree with only one node."""
    return t(1)
