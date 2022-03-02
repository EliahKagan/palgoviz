#!/usr/bin/env python

"""String formatting."""


def mul_table_simple():
    """
    Print a formatted multiplication table from 1-by-1 up to 10-by-10.

    The table has no labels. Numbers are right-justified. Each column has the
    same width as every other column: just enough that every number is preceded
    by at least one space.

    For formatting, this implementation only uses f-strings (or str.format, or
    the format builtin) and the print builtin. The output is not hard-coded.

    >>> mul_table_simple()
       1   2   3   4   5   6   7   8   9  10
       2   4   6   8  10  12  14  16  18  20
       3   6   9  12  15  18  21  24  27  30
       4   8  12  16  20  24  28  32  36  40
       5  10  15  20  25  30  35  40  45  50
       6  12  18  24  30  36  42  48  54  60
       7  14  21  28  35  42  49  56  63  70
       8  16  24  32  40  48  56  64  72  80
       9  18  27  36  45  54  63  72  81  90
      10  20  30  40  50  60  70  80  90 100
    """
    for i in range(1, 11):
        for j in range(1, 11):
            print(f' {i * j:3}', end='')
        print()


def mul_table_simple_alt():
    """
    Print a formatted multiplication table from 1-by-1 up to 10-by-10.

    The table has no labels. Numbers are right-justified. Each column has the
    same width as every other column: just enough that every number is preceded
    by at least one space.

    For formatting, this implementation only uses the % operator and the print
    builtin. The output is not hard-coded.

    >>> mul_table_simple_alt()
       1   2   3   4   5   6   7   8   9  10
       2   4   6   8  10  12  14  16  18  20
       3   6   9  12  15  18  21  24  27  30
       4   8  12  16  20  24  28  32  36  40
       5  10  15  20  25  30  35  40  45  50
       6  12  18  24  30  36  42  48  54  60
       7  14  21  28  35  42  49  56  63  70
       8  16  24  32  40  48  56  64  72  80
       9  18  27  36  45  54  63  72  81  90
      10  20  30  40  50  60  70  80  90 100
    """
    for i in range(1, 11):
        for j in range(1, 11):
            print(' %3d' % (i * j), end='')
        print()


def mul_table(n):
    """
    Print a formatted multiplication table from 1-by-1 up to n-by-n.

    The table has no labels. Numbers are right-justified. Each column has the
    same width as every other column: just enough that every number is preceded
    by at least one space.

    For formatting, this implementation only uses f-strings (or str.format, or
    the format builtin) and the print builtin. It might also call str.

    >>> mul_table(0)
    Traceback (most recent call last):
      ...
    ValueError: n must be strictly positive
    >>> mul_table(1)
     1
    >>> mul_table(3)
     1 2 3
     2 4 6
     3 6 9
    >>> mul_table(9)
      1  2  3  4  5  6  7  8  9
      2  4  6  8 10 12 14 16 18
      3  6  9 12 15 18 21 24 27
      4  8 12 16 20 24 28 32 36
      5 10 15 20 25 30 35 40 45
      6 12 18 24 30 36 42 48 54
      7 14 21 28 35 42 49 56 63
      8 16 24 32 40 48 56 64 72
      9 18 27 36 45 54 63 72 81
    >>> mul_table(10)
       1   2   3   4   5   6   7   8   9  10
       2   4   6   8  10  12  14  16  18  20
       3   6   9  12  15  18  21  24  27  30
       4   8  12  16  20  24  28  32  36  40
       5  10  15  20  25  30  35  40  45  50
       6  12  18  24  30  36  42  48  54  60
       7  14  21  28  35  42  49  56  63  70
       8  16  24  32  40  48  56  64  72  80
       9  18  27  36  45  54  63  72  81  90
      10  20  30  40  50  60  70  80  90 100
    """
    if n < 1:
        raise ValueError('n must be strictly positive')

    width = len(str(n**2))

    for i in range(1, n + 1):
        for j in range(1, n + 1):
            print(f' {i * j:{width}}', end='')
        print()


def mul_table_alt(n):
    """
    Print a formatted multiplication table from 1-by-1 up to n-by-n.

    The table has no labels. Numbers are right-justified. Each column has the
    same width as every other column: just enough that every number is preceded
    by at least one space.

    For formatting, this implementation only uses the % operator and the print
    builtin. It might also call str.

    >>> mul_table_alt(0)
    Traceback (most recent call last):
      ...
    ValueError: n must be strictly positive
    >>> mul_table_alt(1)
     1
    >>> mul_table_alt(3)
     1 2 3
     2 4 6
     3 6 9
    >>> mul_table_alt(9)
      1  2  3  4  5  6  7  8  9
      2  4  6  8 10 12 14 16 18
      3  6  9 12 15 18 21 24 27
      4  8 12 16 20 24 28 32 36
      5 10 15 20 25 30 35 40 45
      6 12 18 24 30 36 42 48 54
      7 14 21 28 35 42 49 56 63
      8 16 24 32 40 48 56 64 72
      9 18 27 36 45 54 63 72 81
    >>> mul_table_alt(10)
       1   2   3   4   5   6   7   8   9  10
       2   4   6   8  10  12  14  16  18  20
       3   6   9  12  15  18  21  24  27  30
       4   8  12  16  20  24  28  32  36  40
       5  10  15  20  25  30  35  40  45  50
       6  12  18  24  30  36  42  48  54  60
       7  14  21  28  35  42  49  56  63  70
       8  16  24  32  40  48  56  64  72  80
       9  18  27  36  45  54  63  72  81  90
      10  20  30  40  50  60  70  80  90 100
    """
    if n < 1:
        raise ValueError('n must be strictly positive')

    width = len(str(n**2))

    for i in range(1, n + 1):
        for j in range(1, n + 1):
            print(' %*d' % (width, i * j), end='')
        print()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
