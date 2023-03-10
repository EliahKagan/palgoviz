# Copyright (c) 2022 David Vassallo and Eliah Kagan
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
Drawing various kinds of object graphs.

Object graphs, also called reference graphs, are graphs with vertices for
objects and directed edges for references.

See also: the objgraph PyPI package.
"""

__all__ = ['draw_one_tuple', 'draw_tuples', 'draw_tuples_alt']

import html

from graphviz import Digraph

from palgoviz import caching


def draw_one_tuple(root):
    """
    Draw the nested tuple structure of an object as a graphviz.Digraph.

    This is a single node if root is an empty tuple or not a tuple. Otherwise,
    the root has children for each of its elements, and their structures are
    recursively drawn according to the same rules.

    Tuples are drawn as points. Non-tuples are drawn as the default oval shape,
    labeled as the repr of the object they stand for. The graph has one node
    per object, regardless of value equality or equality of repr strings.
    """
    return draw_tuples(root)


def draw_tuples(*roots):
    """
    Draw the nested tuple structure of some objects as a graphviz.Digraph.

    The graph is as described in draw_one_tuple, except any number of roots may
    be explored in the traversal. Note that the arguments are roots from which
    traversal proceeds, but not necessarily of the graph produced: the roots of
    the graph are whichever arguments are not reachable from other arguments.

    This implementation uses @memoize_by to maintain visitation information.
    """
    graph = Digraph()

    @caching.memoize_by(id)
    def draw(parent):
        parent_name = str(id(parent))

        if not isinstance(parent, tuple):
            graph.node(parent_name, label=html.escape(repr(parent)))
            return

        graph.node(parent_name, shape='point')
        for child in parent:
            draw(child)
            child_name = str(id(child))
            graph.edge(parent_name, child_name)

    for root in roots:
        draw(root)
    return graph


def draw_tuples_alt(*roots):
    """
    Draw the nested tuple structure of some objects as a graphviz.Digraph.

    The graph is as described in draw_one_tuple, except any number of roots may
    be explored in the traversal. Note that the arguments are roots from which
    traversal proceeds, but not necessarily of the graph produced: the roots of
    the graph are whichever arguments are not reachable from other arguments.

    This alternative implementation manually maintains visitation information.
    """
    graph = Digraph()
    ids = set()

    def draw(parent):
        if id(parent) in ids:
            return

        ids.add(id(parent))
        parent_name = str(id(parent))

        if not isinstance(parent, tuple):
            graph.node(parent_name, label=html.escape(repr(parent)))
            return

        graph.node(parent_name, shape='point')
        for child in parent:
            draw(child)
            child_name = str(id(child))
            graph.edge(parent_name, child_name)

    for root in roots:
        draw(root)
    return graph
