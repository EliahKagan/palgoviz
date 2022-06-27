"""
Drawing various kinds of object graphs.

Object graphs, also called reference graphs, are graphs with vertices for
objects and directed edges for references.

See also: the objgraph PyPI package.

For class inheritance graph drawing, see class_graph.py.

Documented time and space complexities are for n vertices and m edges. In this
module we define auxiliary space as space written to and/or read from that is
allocated by the function (thus outside the input tuple structure), and also
does not belong to the Digraph object being built. That is, we leave out space
belonging to the data structure that is returned to the caller.

Ordinarily one regards all space a function allocates as auxiliary. But this
definition makes sense here because it represents the extra space specifically
associated with the algorithm that performs the traversals.

It's possible to "cheat" by looking into the partially construct Digraph, but
the functions in this module don't do that.
"""

import collections
import html

from graphviz import Digraph

import decorators


def draw_one_tuple(root):
    """
    Draw a nested tuple structure of one object as a graphviz.Digraph.

    This is a single node if root is an empty tuple or not a tuple. Otherwise,
    the root has children for each of its elements, and their structures are
    recursively drawn according to the same rules.

    Tuples are drawn as points. Non-tuples are drawn as the default oval shape,
    labeled as the repr of the object they stand for. The graph has one node
    per object, regardless of value equality or equality of repr strings.

    This has the same asymptotic time and space complexities as draw_tuples and
    draw_tuples_alt.
    """
    return draw_tuples(root)


def draw_tuples(*roots):
    """
    Draw a nested tuple structure of objects as a graphviz.Digraph.

    The graph is as described in draw_one_tuple, except any number of roots may
    be explored in the traversal. Note that the arguments are roots from which
    traversal proceeds, but not necessarily of the graph produced: the roots of
    the graph are whichever arguments are not reachable from other arguments.

    Time complexity is [FIXME: state it]. Auxiliary space complexity as defined
    in the module docstring is [FIXME: state it]. Space taken up by state
    associated with the returned Digraph object is [FIXME: state it].

    This implementation uses @memoize_by to maintain visitation information.
    """
    graph = Digraph()

    @decorators.memoize_by(id)
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
    Draw a nested tuple structure of objects as a graphviz.Digraph.

    The graph is as described in draw_one_tuple, except any number of roots may
    be explored in the traversal. Note that the arguments are roots from which
    traversal proceeds, but not necessarily of the graph produced: the roots of
    the graph are whichever arguments are not reachable from other arguments.

    This alternative implementation manually maintains visitation information.
    It has the same asymptotic time and space complexities as draw_tuples.
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


def draw_tuples_bfs(*roots):
    """
    Draw a nested tuple structure of objects as a graphviz.Digraph. Use BFS.

    This is like draw_tuples/draw_tuples_alt, but breadth-first search (BFS) is
    used instead of depth-first search (DFS). All these functions enumerate
    each vertex's neighbors in the same order, and only tuples are involved so
    the graph is acyclic. So the drawing Graphviz produces often looks the
    same. But this algorithm differs from those: it's iterative, and vertices
    and edges closer to a root are added before any farther from the roots.

    Calling str on the returned graphviz.Digraph object will reveal how the
    order vertices and edges are discovered and emitted is the same in
    draw_tuples and draw_tuples_alt, but different here.

    [FIXME: Do the draw_tuples FIXMEs if not yet done. They're needed below.]

    This has the same asymptotic time and space complexities as draw_tuples and
    draw_tuples_alt. To achieve that auxiliary space (as defined in the module
    docstring), it was necessary to [FIXME: read on, then fill in this blank].
    Otherwise auxiliary space would've been [FIXME: state it]. In contrast,
    recursion.flatten_level_order doesn't do that and wouldn't benefit
    asymptotically, but only by a constant factor, if it did. That's because
    [FIXME: explain the relevant difference].
    """
    graph = Digraph()
    ids = set()
    queue = collections.deque()

    def visit(node):
        if id(node) in ids:
            return

        ids.add(id(node))

        if isinstance(node, tuple):
            graph.node(str(id(node)), shape='point')
            queue.append(node)
        else:
            graph.node(str(id(node)), label=html.escape(repr(node)))

    for root in roots:
        visit(root)

    while queue:
        parent = queue.popleft()
        for child in parent:
            visit(child)
            graph.edge(str(id(parent)), str(id(child)))

    return graph
