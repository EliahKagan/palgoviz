"""
Traversing and drawing graphs of class inheritance.

Inheritance graphs are graphs with vertices for classes (that is, for types)
and directed edges for inheritance relationships.

In general, both conventions for the direction of edges representing
inheritance are common. But all functions in this module regard edges to go
from a base class to a derived class. That's handy for drawing the graphs with
Graphviz, which automatically draws directed graphs with edges pointing
downward from source to destination, when such a layout is feasible.

For (other) object graph drawing, see object_graph.py.
"""

import operator

import graphviz


def _preorder(*, starts, filter, get_neighbors, observe_node, observe_edge):
    if filter is None:
        filter = lambda _: True

    vis = set()

    def explore(src):
        vis.add(src)
        for dest in get_neighbors(src):
            if not filter(dest):
                continue
            observe_edge(src, dest)
            if dest not in vis:
                observe_node(dest)
                explore(dest)

    for start in starts:
        if filter(start) and start not in vis:
            observe_node(start)
            explore(start)


# FIXME: Fix wording. They are not necessarily leaves in the inheritance graph.
#        Maybe rename leaves to starts, too.
def preorder_ancestors(*leaves, filter=None):
    """
    Recursive depth-first preorder traversal from derived to base classes.

    Classes passed as leaves are leaves in the inheritance graph to traverse
    upward in. So they are roots of the traversal itself.

    If filter is not None, it is a predicate called on vertices, including
    those in leaves. If it returns a falsy result on a vertex, neither record
    nor traverse past that vertex.

    Most or all shared logic between this function and dfs_descendants (below)
    should be written in (or extracted to) a module-level nonpublic function.

    Hint: Even though you're returning vertices and edges as separate lists,
    you still have to record vertices before traversing upward from them, to
    ensure ancestors in the traversal (which are descendants in the inheritance
    graph) appear in the returned results before their descendants in the
    traversal (which are their ancestors in the inheritance graph).
    """
    nodes = []
    edges = []

    _preorder(starts=leaves,
              filter=filter,
              get_neighbors=operator.attrgetter('__bases__'),
              observe_node=nodes.append,
              observe_edge=lambda src, dest: edges.append((dest, src)))

    return nodes, edges


# FIXME: Fix wording. They are not necessarily roots in the inheritance graph.
#        Maybe rename roots to starts, too.
def preorder_descendants(*roots, filter=None):
    """
    Recursive depth-first preorder traversal from base to derived classes.

    Classes passed as roots are roots in the inheritance graph to traverse
    downward in. So they are, non-confusingly, roots of the traversal itself.

    If filter is not None, it is a predicate called on vertices, including
    those in leaves. If it returns a falsy result on a vertex, neither record
    nor traverse past that vertex.

    Most or all shared logic between this function and dfs_ancestors (above)
    should be written in (or extracted to) a module-level nonpublic function.

    Hint: Even though you're returning vertices and edges as separate lists,
    you still have to record vertices before traversing downward from them, to
    ensure ancestors in the traversal (which are ancestors in the inheritance
    graph, too) appear in the returned results before their descendants in the
    traversal (which are their ancestors in the inheritance graph, too).
    """
    nodes = []
    edges = []

    _preorder(starts=roots,
              filter=filter,
              get_neighbors=type.__subclasses__,
              observe_node=nodes.append,
              observe_edge=lambda src, dest: edges.append((src, dest)))

    return nodes, edges


def draw(nodes, edges):
    """
    Draw an inheritance graph with the given nodes and edges.

    Nodes (that is, vertices) are classes. Edges are inheritance relationships,
    each pointing from a base class to its (immediately) derived class.

    This returns a graphviz.Digraph rather than displaying anything directly.
    """
    graph = graphviz.Digraph()
    for node in nodes:
        graph.node(str(id(node)), node.__name__)
    for base, derived in edges:
        graph.edge(str(id(base)), str(id(derived)))
    return graph
