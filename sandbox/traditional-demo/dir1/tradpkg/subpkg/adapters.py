# Copyright (c) 2022 David Vassallo and Eliah Kagan
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

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
