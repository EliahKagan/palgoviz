"""Some recursion examples."""

def countdown(n):
    """
    Counts down from n, printing the positive numbers, one per line.

    >>> countdown(10)
    10
    9
    8
    7
    6
    5
    4
    3
    2
    1
    >>> countdown(-1)
    Traceback (most recent call last):
      ...
    ValueError: -1 is less than 0
    """
    if n < 0: 
        raise ValueError(f'{n} is less than 0')
    if n == 0:
        return 
    print(n)
    countdown(n-1)


def add_all(values):
    """
    Adds all the numbers. Like sum(values).

    Assumes values is a sequence (e.g., it can be indexed) of numbers.

    >>> add_all([])
    0
    >>> add_all([7])
    7
    >>> add_all((3, 6, 1))
    10
    """
    result = 0
    for x in values:
        result += x
    return result 

