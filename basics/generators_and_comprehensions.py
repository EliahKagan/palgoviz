"""Generators and comprehensions."""


def my_enumerate(iterable):
    """
    Pair up items in an iterable with indices. Like the built-in enumerate.

    >>> men = my_enumerate(range(3,10000))
    >>> next(men)
    (0, 3)
    >>> next(men)
    (1, 4)
    >>> next(men)
    (2, 5)
    >>> next(men)
    (3, 6)
    >>> list(my_enumerate(['ham', 'spam', 'eggs']))
    [(0, 'ham'), (1, 'spam'), (2, 'eggs')]
    """
    i = 0
    for x in iterable:
        yield (i, x)
        i += 1


def print_enumerated():
    """
    Show the effect of my_enumerate on a sequence of 5, ..., 9 (inclusive).

    >>> print_enumerated()
    index = 0, value = 5
    index = 1, value = 6
    index = 2, value = 7
    index = 3, value = 8
    index = 4, value = 9
    """
    for index, value in my_enumerate(range(5, 10)):
        print (f'{index = }, {value = }')


def print_enumerated_alt():
    """
    Alternative implementation of print_enumerated.

    This uses a generator expression.

    >>> print_enumerated_alt()
    index = 0, value = 5
    index = 1, value = 6
    index = 2, value = 7
    index = 3, value = 8
    index = 4, value = 9
    """
    lines = (f'{index = }, {value = }'
             for index, value
             in my_enumerate(range(5, 10)))
    
    for line in lines:
        print(line)