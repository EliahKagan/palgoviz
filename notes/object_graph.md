<!-- SPDX-License-Identifier: 0BSD -->

# `object_graph` - identified bugs

## Bug #1: Redrawing the edges unnecessarily

Like a visualization of when we didn't memoize.

Repeated problems are being repeated.

That is not what should happen.

*This seems to be fixed by memoizing by `id`.*

## Bug #2: Equal nonidentical objects represented the same

For example, a tuple of five 7s should be 5 separate leaves, if the 7s are
separate objects.

*This was fixed by naming the nodes as their `id`s, converted to strings.*
