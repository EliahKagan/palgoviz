#!/usr/bin/env python

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

import collections
import operator

import graphviz


def _get_filter_or_allow_all(node_filter):
    """Return the filter passed, or an allow-all filter if None is passed."""
    return (lambda _: True) if node_filter is None else node_filter


def _preorder(*, starts, node_filter, get_neighbors,
              observe_node, observe_edge):
    """Generalized preorder DFS traversal with a node filter."""
    vis = set()

    def explore(src):
        vis.add(src)
        for dest in get_neighbors(src):
            if not node_filter(dest):
                continue
            observe_edge(src, dest)
            if dest not in vis:
                observe_node(dest)
                explore(dest)  # Preorder: use the node/edge, THEN explore.

    for start in starts:
        if node_filter(start) and start not in vis:
            observe_node(start)
            explore(start)  # Preorder: use the node/edge, THEN explore.


def _postorder(*, starts, node_filter, get_neighbors,
               observe_node, observe_edge):
    """Generalized postorder DFS traversal with a node filter."""
    vis = set()

    def explore(src):
        vis.add(src)
        for dest in get_neighbors(src):
            if not node_filter(dest):
                continue
            if dest not in vis:
                explore(dest)  # Postorder: explore, THEN use the node/edge.
                observe_node(dest)
            observe_edge(src, dest)

    for start in starts:
        if node_filter(start) and start not in vis:
            explore(start)  # Postorder: explore, THEN use the node/edge.
            observe_node(start)


def _bfs(*, starts, node_filter, get_neighbors, observe_node, observe_edge):
    """Generalized BFS traversal with a node filter."""
    queue = collections.deque(filter(node_filter, starts))
    vis = set(queue)

    while queue:
        src = queue.popleft()
        observe_node(src)
        for dest in get_neighbors(src):
            if not node_filter(dest):
                continue
            observe_edge(src, dest)
            if dest not in vis:
                vis.add(dest)
                queue.append(dest)


def _traverse_ancestors(search, starts, node_filter):
    """Do a derived-to-base search with a generalized traversal function."""
    nodes = []
    edges = []

    search(starts=starts,
           node_filter=_get_filter_or_allow_all(node_filter),
           get_neighbors=operator.attrgetter('__bases__'),
           observe_node=nodes.append,
           observe_edge=lambda src, dest: edges.append((dest, src)))

    return nodes, edges


def _traverse_descendants(search, starts, node_filter):
    """Do a base-to-derived search with a generalized traversal function."""
    nodes = []
    edges = []

    search(starts=starts,
           node_filter=_get_filter_or_allow_all(node_filter),
           get_neighbors=type.__subclasses__,
           observe_node=nodes.append,
           observe_edge=lambda src, dest: edges.append((src, dest)))

    return nodes, edges


def preorder_ancestors(*starts, node_filter=None):
    """
    Recursive depth-first preorder traversal from derived to base classes.

    starts are the starting vertices. Traversal is depth-first from each. The
    search always recurses UP the inheritance graph as far as possible before
    exploring anywhere else. Neighbors are found by checking vertices' direct
    BASE classes, and NEVER by checking derived classes. MROs aren't examined.

    A list of nodes (vertices) and a list of edges are returned. Both lists are
    in discovery order: the order the traversal ADVANCES to them. Even though
    traversal goes from derived to base, each edge is a (base, derived) tuple,
    as in preorder_descendants below.

    If node_filter is not None, it is a predicate called on each vertex found,
    including the starting vertices. If it returns false, the vertex and any
    incident edges are not recorded, and its incident edges are not traversed.
    This lets the caller limit the search.

    Most shared logic between this and preorder_descendants (below) should be
    written in (or extracted to) a module-level nonpublic function.

    >>> from class_graph_examples import D, not_object
    >>> preorder_ancestors(D, node_filter=not_object)
    ([D, B, A, C], [(B, D), (A, B), (C, D), (A, C)])
    """
    return _traverse_ancestors(_preorder, starts, node_filter)


def preorder_descendants(*starts, node_filter=None):
    """
    Recursive depth-first preorder traversal from base to derived classes.

    starts are the starting vertices. Traversal is depth-first from each. The
    search always recurses DOWN the inheritance tree as far as possible before
    exploring anywhere else. Neighbors are found by checking vertices' direct
    DERIVED classes, and NEVER by checking base classes. MROs are not examined.

    A list of nodes (vertices) and a list of edges are returned. Both lists are
    in discovery order: the order the traversal ADVANCES to them. Each edge is
    a (base, derived) tuple.

    If node_filter is not None, it limits the search, as in preorder_ancestors.

    Most shared logic between this and preorder_ancestors (above) should be
    written in (or extracted to) a module-level nonpublic function.

    >>> from class_graph_examples import A
    >>> preorder_descendants(A)
    ([A, B, D, C], [(A, B), (B, D), (A, C), (C, D)])
    """
    return _traverse_descendants(_preorder, starts, node_filter)


def postorder_ancestors(*starts, node_filter=None):
    """
    Recursive depth-first postorder traversal from derived to base classes.

    starts are the starting vertices. Traversal is depth-first from each. The
    search always recurses UP the inheritance graph as far as possible before
    exploring anywhere else. Neighbors are found by checking vertices' direct
    BASE classes, and NEVER by checking derived classes. MROs aren't examined.

    A list of nodes (vertices) and a list of edges are returned. Both lists are
    in the order the traversal RETREATS from them. This is different from the
    order preorder_ancestors emits them, nor usually the reverse of that order,
    because [FIXME: explain why postorder isn't just preorder, reversed]. Even
    though traversal goes from derived to base, each edge is a (base, derived)
    tuple, as in postorder_descendants below.

    If node_filter is not None, it limits the search, as in preorder_ancestors.

    Most shared logic between this and postorder_descendants (below) should be
    written in (or extracted to) a module-level nonpublic function.

    >>> from class_graph_examples import D, not_object
    >>> postorder_ancestors(D, node_filter=not_object)
    ([A, B, C, D], [(A, B), (B, D), (A, C), (C, D)])
    """
    return _traverse_ancestors(_postorder, starts, node_filter)


def postorder_descendants(*starts, node_filter=None):
    """
    Recursive depth-first postorder traversal from base to derived classes.

    starts are the starting vertices. Traversal is depth-first from each. The
    search always recurses DOWN the inheritance tree as far as possible before
    exploring anywhere else. Neighbors are found by checking vertices' direct
    DERIVED classes, and NEVER by checking base classes. MROs are not examined.

    A list of nodes (vertices) and a list of edges are returned. Both lists are
    in the order the traversal RETREATS from them. This is different from the
    order preorder_ancestors emits them, nor usually its reverse (as explained
    in postorder_ancestors). Each edge is a (base, derived) tuple.

    If node_filter is not None, it limits the search, as in preorder_ancestors.

    Most shared logic between this and postorder_ancestors (above) should be
    written in (or extracted to) a module-level nonpublic function.

    >>> from class_graph_examples import A
    >>> postorder_descendants(A)
    ([D, B, C, A], [(B, D), (A, B), (C, D), (A, C)])
    """
    return _traverse_descendants(_postorder, starts, node_filter)


def bfs_ancestors(*starts, node_filter=None):
    """
    Iterative breadth-first traversal (BFS) from derived to base classes.

    starts are the starting vertices. Traversal is breadth-first from each. At
    every point in the search, of vertices not yet found, those that are BASE
    classes of those that have been found will be found before those that are
    not. That is, the search "finds" the start vertices, then finds the start
    vertices' base classes, then finds the start vertices' base classes' base
    classes, and so on. Neighbors are found by checking vertices' direct BASE
    classes, and NEVER by checking derived classes. MROs aren't examined.

    A list of nodes and a list of edges are returned. Both lists are in
    discovery order. Even though traversal goes from derived to base, each edge
    is a (base, derived) tuple, as in bfs_descendants below.

    If node_filter is not None, it limits the search, as in preorder_ancestors.

    Most shared logic between this and bfs_descendants (below) should be
    written in (or extracted to) a module-level nonpublic function.

    >>> from class_graph_examples import D, not_object
    >>> bfs_ancestors(D, node_filter=not_object)
    ([D, B, C, A], [(B, D), (C, D), (A, B), (A, C)])
    """
    return _traverse_ancestors(_bfs, starts, node_filter)


def bfs_descendants(*starts, node_filter=None):
    """
    Iterative breadth-first traversal (BFS) from base to derived classes.

    starts are the starting vertices. Traversal is breadth-first from each. At
    every point in the search, of vertices not yet found, those that are
    DERIVED classes of those that have been found will be found before those
    that are not. That is, the search "finds" the start vertices, then finds
    the start vertices' derived classes, then finds the start vertices' derived
    classes' derived classes, and so on. Neighbors are found by checking
    vertices' direct DERIVED classes, and NEVER by checking base classes. MROs
    aren't examined.

    A list of nodes and a list of edges are returned. Both lists are in
    discovery order. Each edge is a (base, derived) tuple.

    If node_filter is not None, it limits the search, as in preorder_ancestors.

    Most shared logic between this and bfs_ancestors (above) should be written
    in (or extracted to) a module-level nonpublic function.

    >>> from class_graph_examples import A
    >>> bfs_descendants(A)
    ([A, B, C, D], [(A, B), (A, C), (B, D), (C, D)])
    """
    return _traverse_descendants(_bfs, starts, node_filter)


def draw(nodes, edges):
    r"""
    Draw an inheritance graph with the given nodes and edges.

    Nodes (that is, vertices) are classes. Edges are inheritance relationships,
    each pointing from a base class to its (immediately) derived class.

    This returns a graphviz.Digraph rather than displaying anything directly.

    >>> import re; import graphviz; from class_graph_examples import A
    >>> graph = draw(*preorder_descendants(A))
    >>> isinstance(graph, graphviz.Digraph)
    True
    >>> dot_code = str(graph).replace('\t', '    ')
    >>> a, b, c, d = (re.search(fr'(\S+) \[label={label}\]', dot_code).group(1)
    ...               for label in 'ABCD')  # Extract the actual vertex names.
    >>> print(dot_code.replace(a, 'alfa').replace(b, 'bravo')
    ...               .replace(c, 'charlie').replace(d, 'delta'), end='')
    digraph {
        alfa [label=A]
        bravo [label=B]
        delta [label=D]
        charlie [label=C]
        alfa -> bravo
        bravo -> delta
        alfa -> charlie
        charlie -> delta
    }
    """
    graph = graphviz.Digraph()
    for node in nodes:
        graph.node(str(id(node)), node.__name__)
    for base, derived in edges:
        graph.edge(str(id(base)), str(id(derived)))
    return graph


if __name__ == '__main__':
    import doctest
    doctest.testmod()
