"""An "adapter" for converting tuples to "grid" data."""

from .grids import make_grid as _make_grid


def grid_from_coords(m, n, coords):
    """
    Make an m-by-n grid whose (i, j) entry is how many (i, j) appear in coords.

    This adapter converts an iterable of coordinates, coords, to a grid of
    height m and width n, where for each coordinate pair (i, j) in coords, the
    (i, j) entry in the grid is increased by 1. Grid cells that don't
    correspond to any pair of coordinates in coords remain zero.

    Time complexity is O(mn + k), where k = len(coords).
    """
    grid = _make_grid(m, n)

    for i, j in coords:
        grid[i][j] += 1

    return grid
