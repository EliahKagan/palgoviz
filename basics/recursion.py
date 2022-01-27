"""Some recursion examples."""

def countdown(n):
    """
    Count down from n, printing the positive numbers, one per line.

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


def add_all_iterative(values):
    """
    Add all the numbers. Like sum(values).

    Assumes values is a sequence (e.g., it can be indexed) of numbers.

    >>> add_all_iterative([])
    0
    >>> add_all_iterative([7])
    7
    >>> add_all_iterative((3, 6, 1))
    10
    """
    result = 0
    for x in values:
        result += x
    return result 


def add_all_slow(values):
    """
    Add all the numbers recursively. Like sum(values). values is not modified.

    Assumes values is a sequence (e.g., it can be indexed) of numbers.
    >>> add_all_slow(())
    0
    >>> add_all_slow([])
    0
    >>> add_all_slow([7])
    7
    >>> add_all_slow((3, 6, 1))
    10
    >>> values = [2,3,5]
    >>> add_all_slow(values)
    10
    >>> values
    [2, 3, 5]
    """
    match values:
        case []:
            return 0
        case [num, *rest]:
            return num + add_all_slow(rest)   


def add_all(values):
    """
    Add all the numbers recursively. Like sum(values). values is not modified.

    Assumes values is a sequence (e.g., it can be indexed) of numbers.
    >>> add_all(())
    0
    >>> add_all([])
    0
    >>> add_all([7])
    7
    >>> add_all((3, 6, 1))
    10
    >>> values = [2, 3, 5]
    >>> add_all(values)
    10
    >>> values
    [2, 3, 5]
    """
    def add_from(index):
        if index == len(values):
            return 0
        return values[index] + add_from(index + 1)

    return add_from(0)


def linear_search_good(values, x):
    """
    Return an index to some occurrence of x in values, if any. Otherwise return None.
    
    >>> linear_search_good([], 9)
    >>> linear_search_good([2, 3], 2)
    0
    >>> linear_search_good((4, 5, 6), 5)
    1
    """
    try:
       return values.index(x)
    except ValueError: 
        return None


def linear_search_iterative(values, x):
    """
    Return an index to some occurrence of x in values, if any. Otherwise return None.
    
    >>> linear_search_iterative([], 9)
    >>> linear_search_iterative([2, 3], 2)
    0
    >>> linear_search_iterative((4, 5, 6), 5)
    1
    """
    for index, value in enumerate(values):
        if value == x:
            return index
    return None  

def linear_search(values, x):
    """
    Return an index to some occurrence of x in values, if any. Otherwise return None.
    
    >>> linear_search([], 9)
    >>> linear_search([2, 3], 2)
    0
    >>> linear_search((4, 5, 6), 5)
    1
    """
    def search_from(index): 
        if index == len(values): 
            return None
        if values[index] == x: 
            return index
        return search_from(index + 1)
    return search_from(0)