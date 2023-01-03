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

"""
Small examples of binary trees that are almost but not quite BSTs.

These examples are mainly for testing tree.is_bst, tree.is_bst_alt, and
tree.is_bst_iterative. But they can be used for exploration or other purposes.
"""


def small(t):
    """Make a 7-node not-quite-BST of minimal height."""
    return t(4, t(2, t(1), t(3)), t(5, t(6), t(7)))


def small_str(t):
    """Make a 7-node not-quite-BST of minimal height."""
    return t('salamander',
             t('lizard', t('iguana'), t('newt')),
             t('snake', t('tortoise'), t('turtle')))


def lefty(t):
    """
    Make a 9-node not-quite-BST of maximum depth, alternating left and right.
    """
    return t(8, t(6, t(4, t(2, t(1), t(3)), t(7)), t(7)), t(9))


def righty(t):
    """
    Make a 9-node not-quite_BST of maximum depth, alternating left and right.
    """
    return t(2, t(1), t(4, t(1), t(6, t(5), t(8, t(7), t(9)))))


def medium(t):
    """
    Make a mostly balanced 24-node not-quite-BST with a few duplicate elements.
    """
    # The noqa are for "continuation line over-indented for visual indent".
    return t(11, t(4,  t(2,  t(1, t(1), t(2)),
                             t(3, None, t(3))),     # noqa: E127
                       t(8,  t(6, t(3), t(7)),      # noqa: E127
                             t(10, t(9), None))),   # noqa: E127
                 t(15, t(13, t(12), t(14)),         # noqa: E127
                       t(19, t(17, t(16), t(18)),   # noqa: E127
                             t(20, None, t(21)))))  # noqa: E127
