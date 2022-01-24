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
