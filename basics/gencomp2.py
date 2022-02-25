#!/usr/bin/env python

"""
More generators and comprehensions.

See also gencomp1.py.
"""


def _dimensions(a):
    height = len(a)
    if height == 0:
        raise ValueError('empty matrix not supported')

    width = len(a[0])
    if any(len(row) != width for row in a):
        raise ValueError('a jagged grid is not a matrix')
    if width == 0:
        raise ValueError('empty rows not supported')

    return height, width


def matrix_multiply(a, b):
    a_height, a_width = _dimensions(a)
    b_height, b_width = _dimensions(b)

    if a_width != b_height:
        raise ValueError(f"can't multiply {a_height}x{a_width} by"
                         f" {b_height}x{b_width} matrices")

    return [[sum(a[i][j] * b[j][k] for j in range(a_width))
             for i in range(a_height)]
            for k in range(b_width)]
