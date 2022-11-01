#!/usr/bin/env python

"""
Functions used in subproblems_wip.ipynb. Extracted from recursion.py.

These functions are not of great enough interest to remain in recursion.py, and
the exercises they serve did not work out and have been scrapped (with a hope
that some of the material may be reusable in some way).

But some of the drawings those exercises produced are interesting and
illuminating, so for now, subproblems_wip.ipynb is retained, modified to use
the functions it said to add to recursion.py from this module instead.
"""

import collections

from algoviz.recursion import merge_two


def observe_node(node):
    """
    Print a representation of a node in a tree.

    This is a simple node observer. It prefixes "node:" to distinguish its
    output from other output.
    """
    print(f'node:  {node!r}')


def observe_edge_verbose(parent, child):
    """
    Print a labeled representation of an edge from parent to child in a tree.

    This is like recursion.observe_edge, but "edge:" is prepended.
    """
    print(f'edge:  {parent!r}  ->  {child!r}')


def merge_sort_observed(values, *, merge=merge_two,
                        node_observer, edge_observer):
    """
    Mergesort recursively. Notify observers of subproblem relationships.

    Observers are called while advancing, during splitting. See description and
    usage in subproblems.ipynb (Mergesort - Drawing subproblem trees).

    NOTE: node_observer must always called for each subproblem input exactly
    once, and no object is passed as either argument to edge_observer until
    after it has been passed to node_observer.

    >>> merge_sort_observed([3, 2, 1],
    ...                     node_observer=observe_node,
    ...                     edge_observer=observe_edge_verbose)
    node:  [3, 2, 1]
    node:  [3]
    edge:  [3, 2, 1]  ->  [3]
    node:  [2, 1]
    edge:  [3, 2, 1]  ->  [2, 1]
    node:  [2]
    edge:  [2, 1]  ->  [2]
    node:  [1]
    edge:  [2, 1]  ->  [1]
    [1, 2, 3]
    """
    def do_mergesort(parent, node):
        node_observer(node)
        if parent is not None:
            edge_observer(parent, node)

        if len(node) < 2:
            return node

        midpoint = len(node) // 2
        left = node[:midpoint]
        right = node[midpoint:]
        return merge(do_mergesort(node, left), do_mergesort(node, right))

    return do_mergesort(None, list(values))


def merge_sort_bottom_up_unstable_observed(values, *, merge=merge_two,
                                           node_observer, edge_observer):
    """
    Unstable bottom-up mergesort. Notify observers of subproblem relationships.

    This reports subproblems in an order unchanged by merge operations. This is
    the order in which they would be split, if this were a top-down algorithm,
    and facilitates comparison to observations mach of such implementations.
    This is to say that the lists shown in the subproblems tree will often be
    lists that merge_sort_bottom_up_unstable would never have created. See
    subproblems.ipynb (Mergesort - Drawing subproblem trees).

    NOTE: node_observer must always called for each subproblem input exactly
    once, and no object is passed as either argument to edge_observer until
    after it has been passed to node_observer.

    >>> merge_sort_bottom_up_unstable_observed(
    ...     [3, 2, 1],
    ...     node_observer=observe_node,
    ...     edge_observer=observe_edge_verbose)
    node:  [3]
    node:  [2]
    node:  [1]
    node:  [3, 2]
    edge:  [3, 2]  ->  [3]
    edge:  [3, 2]  ->  [2]
    node:  [1, 3, 2]
    edge:  [1, 3, 2]  ->  [1]
    edge:  [1, 3, 2]  ->  [3, 2]
    [1, 2, 3]
    """
    if not values:
        return []

    queue = collections.deque([x] for x in values)

    sham_queue = collections.deque([x] for x in values)
    for node in sham_queue:
        node_observer(node)

    while len(queue) > 1:
        left = queue.popleft()
        right = queue.popleft()
        queue.append(merge(left, right))

        sham_left = sham_queue.popleft()
        sham_right = sham_queue.popleft()
        sham_parent = sham_left + sham_right

        node_observer(sham_parent)
        edge_observer(sham_parent, sham_left)
        edge_observer(sham_parent, sham_right)

        sham_queue.append(sham_parent)

    return queue[0]


def merge_sort_bottom_up_observed(values, *, merge=merge_two,
                                  node_observer, edge_observer):
    """
    Stable bottom-up mergesort. Notify observers of subproblem relationships.

    See subproblems.ipynb (Mergesort - Drawing subproblem trees).

    NOTE: node_observer must always called for each subproblem input exactly
    once, and no object is passed as either argument to edge_observer until
    after it has been passed to node_observer.

    >>> merge_sort_bottom_up_observed([3, 2, 1],
    ...                               node_observer=observe_node,
    ...                               edge_observer=observe_edge_verbose)
    node:  [3]
    node:  [2]
    node:  [1]
    node:  [3, 2]
    edge:  [3, 2]  ->  [3]
    edge:  [3, 2]  ->  [2]
    node:  [3, 2, 1]
    edge:  [3, 2, 1]  ->  [3, 2]
    edge:  [3, 2, 1]  ->  [1]
    [1, 2, 3]
    """
    if not values:
        return []

    primary = collections.deque([x] for x in values)
    secondary = collections.deque()
    sham_primary = collections.deque([x] for x in values)
    sham_secondary = collections.deque()

    for node in sham_primary:
        node_observer(node)

    while len(primary) > 1:
        primary, secondary = secondary, primary
        sham_primary, sham_secondary = sham_secondary, sham_primary

        while len(secondary) > 1:
            left = secondary.popleft()
            right = secondary.popleft()
            primary.append(merge(left, right))

            sham_left = sham_secondary.popleft()
            sham_right = sham_secondary.popleft()
            sham_parent = sham_left + sham_right

            node_observer(sham_parent)
            edge_observer(sham_parent, sham_left)
            edge_observer(sham_parent, sham_right)

            sham_primary.append(sham_parent)

        if secondary:
            primary.append(secondary.popleft())
            sham_primary.append(sham_secondary.popleft())

    return primary[0]


__all__ = [thing.__name__ for thing in (
    observe_node,
    observe_edge_verbose,
    merge_sort_observed,
    merge_sort_bottom_up_unstable_observed,
    merge_sort_bottom_up_observed,
)]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
