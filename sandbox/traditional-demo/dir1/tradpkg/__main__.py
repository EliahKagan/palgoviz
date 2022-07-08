"""
Print a grid.

This demonstrates running the top-level package as a script.
"""

from .subpkg.grids import make_grid

print(make_grid(4, 4))