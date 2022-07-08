"""
Print a grid.

This demonstrates running the top-level package as a script.
"""

from . import subpkg

print(subpkg.grids.make_grid(4, 4))