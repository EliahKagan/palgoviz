"""
Drawing various kinds of object graphs.

Object graphs, also called reference graphs, are graphs with vertices for
objects and directed edges for references.

See also: the objgraph PyPI package.

For drawing class inheritance graphs, see class_graph.py.

Documented time and space complexities are for n vertices and m edges. In this
module we define auxiliary space as space allocated by the function (thus
outside the input tuple structure) but not belonging to the Digraph object
being built. Ordinarily we would regard all space a function allocates to be
auxiliary. The alternative definition used here is useful because it represents
just the extra space used by the traversal itself. It's possible to "cheat" by
examining the partially built Digraph, but the functions here don't do that.
"""

__all__ = [
    'draw_one_tuple',
    'draw_tuples',
    'draw_tuples_alt',
    'draw_tuples_bfs',
]

import collections
import html

from graphviz import Digraph

import caching


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

    This algorithm is a hybrid of preorder and postorder DFS: [FIXME: explain].
    Time complexity is [FIXME: state it]. Auxiliary space complexity as defined
    in the module docstring is [FIXME: state it]. Space taken up by the emitted
    data (associated with the returned Digraph object) is [FIXME: state it].

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
    Draw a nested tuple structure of objects as a graphviz.Digraph.

    The graph is as described in draw_one_tuple, except any number of roots may
    be explored in the traversal. Note that the arguments are roots from which
    traversal proceeds, but not necessarily of the graph produced: the roots of
    the graph are whichever arguments are not reachable from other arguments.

    This alternative implementation manually maintains visitation information.
    It is an alternative implementation strategy for the same algorithm. So it
    has the same asymptotic time and space complexities as draw_tuples.
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
    each vertex's neighbors in the same order, and the graph is acyclic since
    only tuples are involved. So the drawing Graphviz produces often looks the
    same. But this algorithm differs from those: it's iterative, and vertices
    and edges closer to a root are added before any farther from the roots.

    Calling str on the returned Digraph object and examining the resulting DOT
    code reveals how the order vertices and edges are discovered and emitted is
    the same in draw_tuples and draw_tuples_alt, but different here.

    FIXME: Do the draw_tuples FIXMEs if not yet done. They're needed below.

    Asymptotic time and space are as in draw_tuples/draw_tuples_alt. To match
    that auxiliary space here, it was necessary to [FIXME: say what had to be
    done], or auxiliary space would be [FIXME: state it] instead.

    Yet recursion.flatten_level_order doesn't do that. If it did, it would
    benefit only by a constant factor, not asymptotically. That's because
    [FIXME: explain the relevant difference between that and this situation].
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
