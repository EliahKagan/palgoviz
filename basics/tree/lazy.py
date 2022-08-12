#!/usr/bin/env python

"""
Special-purpose lazy trees.

>>> root = node = LazyNode(1, 2**10_000)
>>> while node:
...     node = node.left
...     if node: node = node.right
>>> root.get_size_computed()
10000
"""


class LazyNode:
    """
    A node in a BST of consecutive integers, constructing branches on demand.

    >>> root = LazyNode(1, 16)
    >>> root.get_size_computed()
    1
    >>> root.element
    8
    >>> root.get_size_computed()
    1
    >>> root.left.element
    4
    >>> root.get_size_computed()
    2
    >>> root.left.right.element
    6
    >>> root.get_size_computed()
    3
    """

    __slots__ = ('_low', '_high', '_left', '_right')

    def __new__(cls, low, high):
        """Create a new node in a lazy binary search tree, or return None."""
        if not isinstance(low, int):
            raise TypeError(f"low must be 'int', got {type(low).__name__!r}")
        if not isinstance(high, int):
            raise TypeError(f"high must be 'int', got {type(high).__name__!r}")
        if low > high:
            raise ValueError('low (got {low!r}) exceeds high (got {high!r})')
        if low == high:
            return None  # Empty branch.

        node = super().__new__(cls)
        node._low = low
        node._high = high
        return node

    def __repr__(self):
        """Python code representation of this lazy binary search tree node."""
        return f'{type(self).__name__}({self.low!r}, {self.high!r})'

    @property
    def low(self):
        """The inclusive lower bound of the range of this node's subtree."""
        return self._low

    @property
    def high(self):
        """The exclusive upper bound of the range of this node's subtree."""
        return self._high

    @property
    def element(self):
        """The element held at this node: the midpoint between low and high."""
        return (self.low + self.high) // 2

    @property
    def left(self):
        """This node's left child. Computed on first access."""
        try:
            return self._left
        except AttributeError:
            self._left = type(self)(self.low, self.element)
            return self._left

    @property
    def right(self):
        """This node's right child. Computed on first access."""
        try:
            return self._right
        except AttributeError:
            self._right = type(self)(self.element + 1, self.high)
            return self._right

    def get_size_computed(self):
        """Count how many nodes of this (sub)tree have been constructed."""
        count = 0
        stack = [self]

        while stack:
            count += 1
            parent = stack.pop()

            # Traverse to children if they are computed and not None.
            if left := getattr(parent, '_left', None):
                stack.append(left)
            if right := getattr(parent, '_right', None):
                stack.append(right)

        return count


if __name__ == '__main__':
    import doctest
    doctest.testmod()
