"""
Drawing bipartite contact tracing graphs.

A bipartite graph is a graph whose vertices can be partitioned into two sets,
such that each edge connects a vertex in one set to a vertex in the other:

    https://en.wikipedia.org/wiki/Bipartite_graph

One way bipartite graphs arise is when vertices represent two different kinds
of things, and edges represent relationships that are only meaningful between
something of one kind and something of the other kind.

This module continues the story of woe that began in enumerations.Guests.
"""

__all__ = ['draw_network']

import html
import itertools

import graphviz

from palgoviz import gencomp1


def _do_draw_network(events):
    """Helper for draw_network. Assumes materialization and safe names."""
    graph_attr = dict(overlap='voronoi')
    graph = graphviz.Graph(graph_attr=graph_attr)
    graph.engine = 'sfdp'
    graph.strict = True

    # Add each event vertex exactly once, in the order in which they appear.
    for event in events:
        graph.node(event, shape='egg', style='filled', fillcolor='pink')

    # Add each guest vertex exactly once, in the order in which they appear.
    guests = gencomp1.distinct(itertools.chain.from_iterable(events.values()))
    for guest in guests:
        graph.node(guest, shape='box', style='filled', fillcolor='lightblue')

    # Add all edges, in the order in which they appear.
    for event, guests in events.items():
        for guest in guests:
            graph.edge(event, guest)

    return graph


def draw_network(**events):
    """
    Draw a contact tracing graph of events attended by potential umpires.

    It's bad enough that the parties went too far, and the criminal justice
    system got involved, but it turns out the guests are also the center of an
    epidemic of umpirism. The crowded environment of a wild party, or an even
    wilder trial, is the perfect setting for any umpire in attendance to
    inadvertently cause anyone else to become an umpire.

    At this point, it's unknown who was an umpire when or for how long, so
    we're just drawing an undirected graph with edges between each guest and
    each event that guest attended. By inspecting the graph, one can see all
    guests who attended any event and all events any guest attended. Guests a
    distance 2 apart in the graph attended at least one common event.

    Guests and events are vertices. Guest vertices' shapes and colors differ
    from event vertices' shapes and colors, to avoid confusion. Each event is
    passed as a keyword argument, where the argument name is the name of the
    event, and the argument value is an iterable of strings naming the guests.
    This does not use enumerations.Guests, and guests and events are not
    limited to those represented in it. There is no way to specify a guest who
    attended no events of interest, since such a guest is likewise not of
    interest. If an event has no guests, [FIXME: decide what to do]. If an
    event lists the same guest twice, [FIXME: decide what to do].

    This returns a graphviz.Graph instead of displaying anything directly. See
    umpire.ipynb.

    FIXME: Try out all eight layout engines, and some ways of eliminating
    overlap (at least "prism" and "voronoi"), to see what looks best.
      - https://graphviz.org/docs/layouts/
      - https://graphviz.org/docs/attrs/overlap/
    You may also want to try out several combinations of node shapes.
    """
    return _do_draw_network({
        html.escape(event): [html.escape(guest) for guest in guests]
        for event, guests in events.items()
    })
