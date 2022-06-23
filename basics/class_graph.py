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


def preorder_ancestors(*starts, filter=None):
    """
    Recursive depth-first preorder traversal from derived to base classes.

    starts are the starting vertices. Traversal is depth-first from each. The
    search recursively goes UP the inheritance graph as far as possible before
    exploring anywhere else. Neighbors are found by checking vertices' direct
    base classes, and NEVER by checking derived classes. MROs aren't examined.

    A list of nodes (vertices) and a list of edges are returned. Both lists are
    in discovery order: the order the traversal ADVANCES to them. Even though
    traversal goes derived to base, each edge is a (base, derived) tuple, as in
    preorder_descendants below.

    If filter is not None, it is a predicate called on each vertex found,
    including the starting vertices. If it returns false, the vertex is neither
    emitted nor traversed through. This lets the caller limit the search.

    Most or all shared logic between this and preorder_descendants (below)
    should be written in (or extracted to) a module-level nonpublic function.
    """
    nodes = []
    edges = []

    _preorder(starts=starts,
              filter=filter,
              get_neighbors=operator.attrgetter('__bases__'),
              observe_node=nodes.append,
              observe_edge=lambda src, dest: edges.append((dest, src)))

    return nodes, edges


def preorder_descendants(*starts, filter=None):
    """
    Recursive depth-first preorder traversal from base to derived classes.

    starts are the starting vertices. Traversal is depth-first from each. The
    search recursively goes DOWN the inheritance tree as far as possible before
    exploring anywhere else. Neighbors are found by checking vertices' direct
    derived classes, and NEVER by checking base classes. MROs are not examined.

    A list of nodes (vertices) and a list of edges are returned. Both lists are
    in discovery order: the order the traversal ADVANCES to them. Each edge is
    a (base, derived) tuple.

    If filter is not None, it limits the search, as in preorder_ancestors.

    Most or all shared logic between this and preorder_ancestors (above) should
    be written in (or extracted to) a module-level nonpublic function.
    """
    nodes = []
    edges = []

    _preorder(starts=starts,
              filter=filter,
              get_neighbors=type.__subclasses__,
              observe_node=nodes.append,
              observe_edge=lambda src, dest: edges.append((src, dest)))

    return nodes, edges


def postorder_ancestors(*starts, filter=None):
    """
    Recursive depth-first postorder traversal from derived to base classes.

    starts are the starting vertices. Traversal is depth-first from each. The
    search recursively goes UP the inheritance graph as far as possible before
    exploring anywhere else. Neighbors are found by checking vertices' direct
    base classes, and NEVER by checking derived classes. MROs aren't examined.

    A list of nodes (vertices) and a list of edges are returned. Both lists are
    in the order the traversal RETREATS from them. This is different from the
    order preorder_ancestors emits them. But not usually the reverse of that
    order, because [FIXME: explain why postorder isn't just preorder reversed].
    Even though traversal goes derived to base, each edge is (base, derived)
    tuple, as in postorder_descendants below.

    If filter is not None, it limits the search, as in preorder_ancestors.

    Most or all shared logic between this and postorder_descendants (below)
    should be written in (or extracted to) a module-level nonpublic function.
    """
    # FIXME: Needs implementation.


def postorder_descendants(*starts, filter=None):
    """
    Recursive depth-first postorder traversal from base to derived classes.

    starts are the starting vertices. Traversal is depth-first from each. The
    search recursively goes DOWN the inheritance tree as far as possible before
    exploring anywhere else. Neighbors are found by checking vertices' direct
    derived classes, and NEVER by checking base classes. MROs are not examined.

    A list of nodes (vertices) and a list of edges are returned. Both lists are
    in the order the traversal RETREATS from them. This is different from the
    order preorder_ancestors emits them, and not usually the reverse (see
    postorder_ancestors for details). Each edge is (base, derived) tuple.

    If filter is not None, it limits the search, as in preorder_ancestors.

    Most or all shared logic between this and postorder_ancestors (above)
    should be written in (or extracted to) a module-level nonpublic function.
    """
    # FIXME: Needs implementation.


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
