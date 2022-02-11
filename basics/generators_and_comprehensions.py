"""Generators and comprehensions."""


def my_enumerate(iterable, start=0):
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
    >>> men = my_enumerate(range(3,10000), 3)
    >>> next(men)
    (3, 3)
    >>> next(men)
    (4, 4)
    >>> next(men)
    (5, 5)
    >>> next(men)
    (6, 6)
    >>> list(my_enumerate(['ham', 'spam', 'eggs'], 10))
    [(10, 'ham'), (11, 'spam'), (12, 'eggs')]
    """
    for x in iterable:
        yield (start, x)
        start += 1


def print_enumerated(*, start=0): # start is now a keyword only argument, meaning that user MUST use in the form print_enumerated(start=n)
    """
    Show the effect of my_enumerate on a sequence of 5, ..., 9 (inclusive).

    >>> print_enumerated()
    index = 0, value = 5
    index = 1, value = 6
    index = 2, value = 7
    index = 3, value = 8
    index = 4, value = 9
    >>> print_enumerated(start=7)
    index = 7, value = 5
    index = 8, value = 6
    index = 9, value = 7
    index = 10, value = 8
    index = 11, value = 9
    """
    for index, value in my_enumerate(range(5, 10), start):
        print (f'{index = }, {value = }')


def print_enumerated_alt(*, start=0):
    """
    Alternative implementation of print_enumerated.

    This uses a generator expression.

    >>> print_enumerated_alt()
    index = 0, value = 5
    index = 1, value = 6
    index = 2, value = 7
    index = 3, value = 8
    index = 4, value = 9
    >>> print_enumerated_alt(start=7)
    index = 7, value = 5
    index = 8, value = 6
    index = 9, value = 7
    index = 10, value = 8
    index = 11, value = 9
    """
    lines = (f'{index = }, {value = }'
             for index, value
             in my_enumerate(range(5, 10), start))

    for line in lines:
        print(line)


def my_any(iterable):
    """
    Test if any element of an iterable is truthy.

    >>> my_any([])
    False
    >>> my_any([17, 4, 9, 0, 3, 5, 0])
    True
    >>> my_any(x % 17 == 0 for x in range(100))
    True
    >>> my_any(x > 100 for x in range(100))
    False
    """
    for element in iterable:
        if element: return True
    return False


def my_all(iterable):
    """
    Tell if all elements of an iterable are truthy.

    >>> my_all([])
    True
    >>> my_all([17, 4, 9, 0, 3, 5, 0])
    False
    >>> my_all(x % 17 == 0 for x in range(100))
    False
    >>> my_all(x > 100 for x in range(100))
    False
    >>> my_all(x % 17 == 0 for x in range(0, 100, 17))
    True
    >>> my_all([1])
    True
    >>> my_all([1, 1, 1, 6, 7])
    True
    """
    for element in iterable:
        if not element: return False
    return True


def zip_two(first, second):
    """
    Zips two iterables.

    Zips shortest, like the built-in zip, but must take exactly 2 arguments.

    >>> list(zip_two([], []))
    []
    >>> list(zip_two([10, 20], []))
    []
    >>> list(zip_two([], [30, 40]))
    []

    >>> ordered = ['gaming mouse', 'mechanical keyboard', '4k monitor']
    >>> received = ['bobcat', 'larger bobcat', 'gigantic bobcat']
    >>> for order, got in zip_two(ordered, received):
    ...     print(f'I ordered a {order} but I got a {got} instead!')
    I ordered a gaming mouse but I got a bobcat instead!
    I ordered a mechanical keyboard but I got a larger bobcat instead!
    I ordered a 4k monitor but I got a gigantic bobcat instead!

    >>> ordered = ['gaming mouse', 'mechanical keyboard', '4k monitor']
    >>> received = ['bobcat', 'larger bobcat']
    >>> for order, got in zip_two(ordered, received):
    ...     print(f'I ordered a {order} but I got a {got} instead!')
    I ordered a gaming mouse but I got a bobcat instead!
    I ordered a mechanical keyboard but I got a larger bobcat instead!

    >>> ordered = ['gaming mouse', 'mechanical keyboard']
    >>> received = ['bobcat', 'larger bobcat', 'gigantic bobcat']
    >>> for order, got in zip_two(ordered, received):
    ...     print(f'I ordered a {order} but I got a {got} instead!')
    I ordered a gaming mouse but I got a bobcat instead!
    I ordered a mechanical keyboard but I got a larger bobcat instead!

    >>> ordered = ['gaming mouse', 'mechanical keyboard', '4k monitor']
    >>> bobcats = ['bobcat', 'larger bobcat', 'gigantic bobcat']
    >>> received = (cat.upper() for cat in bobcats)
    >>> for order, got in zip_two(ordered, received):
    ...     print(f'I ordered a {order} but I got a {got} instead!')
    I ordered a gaming mouse but I got a BOBCAT instead!
    I ordered a mechanical keyboard but I got a LARGER BOBCAT instead!
    I ordered a 4k monitor but I got a GIGANTIC BOBCAT instead!
    """
    f = iter(first)
    s = iter(second)
    while True:
        try:
            yield (next(f), next(s))
        except StopIteration:
            return


def my_zip(*iterables):
    """
    Zips two iterables. Like the built-in zip, but with no "strict" argument.

    >>> list(my_zip([], []))
    []
    >>> list(my_zip([10, 20], []))
    []
    >>> list(my_zip([], [30, 40]))
    []
    >>> list(my_zip([]))
    []
    >>> list(my_zip(()))
    []
    >>> list(my_zip([10]))
    [(10,)]
    >>> list(my_zip())
    []

    >>> ordered = ['gaming mouse', 'mechanical keyboard', '4k monitor']
    >>> received = ['bobcat', 'larger bobcat', 'gigantic bobcat']
    >>> for order, got in my_zip(ordered, received):
    ...     print(f'I ordered a {order} but I got a {got} instead!')
    I ordered a gaming mouse but I got a bobcat instead!
    I ordered a mechanical keyboard but I got a larger bobcat instead!
    I ordered a 4k monitor but I got a gigantic bobcat instead!

    >>> ordered = ['gaming mouse', 'mechanical keyboard', '4k monitor']
    >>> received = ['bobcat', 'larger bobcat']
    >>> for order, got in my_zip(ordered, received):
    ...     print(f'I ordered a {order} but I got a {got} instead!')
    I ordered a gaming mouse but I got a bobcat instead!
    I ordered a mechanical keyboard but I got a larger bobcat instead!

    >>> ordered = ['gaming mouse', 'mechanical keyboard']
    >>> received = ['bobcat', 'larger bobcat', 'gigantic bobcat']
    >>> for order, got in my_zip(ordered, received):
    ...     print(f'I ordered a {order} but I got a {got} instead!')
    I ordered a gaming mouse but I got a bobcat instead!
    I ordered a mechanical keyboard but I got a larger bobcat instead!

    >>> ordered = ['gaming mouse', 'mechanical keyboard', '4k monitor']
    >>> bobcats = ['bobcat', 'larger bobcat', 'gigantic bobcat']
    >>> received = (cat.upper() for cat in bobcats)
    >>> for order, got in my_zip(ordered, received):
    ...     print(f'I ordered a {order} but I got a {got} instead!')
    I ordered a gaming mouse but I got a BOBCAT instead!
    I ordered a mechanical keyboard but I got a LARGER BOBCAT instead!
    I ordered a 4k monitor but I got a GIGANTIC BOBCAT instead!

    >>> ordered = ['gaming mouse', 'mechanical keyboard', '4k monitor']
    >>> received = (cat.upper() for cat in bobcats)
    >>> grunts = ['Doh!', 'Ow!', 'OOF!']
    >>> for grunt, order, got in my_zip(grunts, ordered, received):
    ...     print(f'{grunt} I ordered a {order} but I got a {got} instead!')
    Doh! I ordered a gaming mouse but I got a BOBCAT instead!
    Ow! I ordered a mechanical keyboard but I got a LARGER BOBCAT instead!
    OOF! I ordered a 4k monitor but I got a GIGANTIC BOBCAT instead!

    >>> ordered = ['gaming mouse', 'mechanical keyboard']
    >>> received = (cat.upper() for cat in bobcats)
    >>> grunts = ['Doh!', 'Ow!', 'OOF!']
    >>> for grunt, order, got in my_zip(grunts, ordered, received):
    ...     print(f'{grunt} I ordered a {order} but I got a {got} instead!')
    Doh! I ordered a gaming mouse but I got a BOBCAT instead!
    Ow! I ordered a mechanical keyboard but I got a LARGER BOBCAT instead!
    """
    if not iterables: # check if there are no arguments
        return

    iterators = [iter(arg) for arg in iterables]

    while True:
        try:
            # Use a list comprehension so we can catch StopIteration from it.
            yield tuple([next(it) for it in iterators])
        except StopIteration:
            return


def print_zipped():
    """
    Zip two enumerated things with my_enumerate and zip_two and print elements.

    >>> print_zipped()
    word_index=1, word='bat', number_index=100, number=1.5
    word_index=2, word='dog', number_index=101, number=2.5
    word_index=3, word='cat', number_index=102, number=3.5
    word_index=4, word='horse', number_index=103, number=4.5
    """
    words = ['bat', 'dog', 'cat', 'horse']
    numbers = [1.5, 2.5, 3.5, 4.5]
    zipped = zip_two(my_enumerate(words, 1), my_enumerate(numbers, 100))

    for (word_index, word), (number_index, number) in zipped:
        print(f'{word_index=}, {word=}, {number_index=}, {number=}')


# TODO: When we do unittest and pytest, translate these doctests and observe
#       how much clearer (and easier to get right) they are.
def fib_n(n):
    """
    Return an iterator that yields the first n Fibonacci numbers.

    >>> next(fib_n(0))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> it = fib_n(1)
    >>> next(it)
    0
    >>> next(it)
    Traceback (most recent call last):
      ...
    StopIteration
    >>> it = fib_n(2)
    >>> next(it)
    0
    >>> next(it)
    1
    >>> next(it)
    Traceback (most recent call last):
      ...
    StopIteration
    >>> list(fib_n(3))
    [0, 1, 1]
    >>> list(fib_n(4))
    [0, 1, 1, 2]
    >>> list(fib_n(7))
    [0, 1, 1, 2, 3, 5, 8]
    >>> list(fib_n(16))
    [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610]
    >>> list(fib_n(101))[-1]
    354224848179261915075
    >>> fib_n(-1)
    Traceback (most recent call last):
      ...
    ValueError: can't yield negatively many Fibonacci numbers
    >>> fib_n(1.0)
    Traceback (most recent call last):
      ...
    TypeError: n must be an int
    >>> list(fib_n(True))  # OK, since bool is a subclass of int.
    [0]
    """
    if not isinstance(n, int):
        raise TypeError(f'n must be an int')
    if n < 0:
        raise ValueError(f"can't yield negatively many Fibonacci numbers")

    def generate():
        a = 0
        b = 1
        for _ in range(n):
            yield a
            a, b = b, a + b

    return generate()
