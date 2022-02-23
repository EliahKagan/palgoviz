"""
Drawing various kinds of object graphs.

Object graphs, also called reference graphs, are graphs with vertices for
objects and directed edges for references.

See also: the objgraph PyPI package.
"""

import html

import graphviz


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
    """
    graph = graphviz.Digraph()
    visited_ids = set()

    def draw(node):
        if id(node) in visited_ids:
            return

        visited_ids.add(id(node))

        if not isinstance(node, tuple):
            graph.node(str(id(node)), label=html.escape(repr(node)))
            return

        graph.node(str(id(node)), shape='point')

        for child in node:
            draw(child)
            graph.edge(str(id(node)), str(id(child)))

    for root in roots:
        draw(root)

    return graph
