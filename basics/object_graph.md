# `object_graph` - identified bugs

## Bug #1: Redrawing the edges unnecessarily.

Like a visualization of when we didn't memoize.

Repeated problems are being repeated.

That is not what should happen.


## Bug #2: If objects are value equal but not the same object, they are not being represented differently.

For example, a tuple of five 7s should be 5 separate leaves, if the 7s are separate objects.
