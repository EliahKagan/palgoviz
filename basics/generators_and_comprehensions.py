"""Generators and comprehensions."""


from operator import truediv


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
    >>> list(fib_n(1))
    [0]
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
    if n < 0:
        raise ValueError(f"can't yield negatively many Fibonacci numbers")

    if not isinstance(n, int):
        raise TypeError('n must be an int')

    def helpf():
        first = 0
        second = 1
        for _ in range(n):
            yield first
            first, second = second, first + second

    return helpf()


def map_one(func, iterable):
    """
    Map values from the given interable through the unary function func.

    This is like the builtin map, except it doesn't accept multiple iterables.

    That is, map accepts an n-ary function and n iterable arguments, but
    map_one requires a unary function and exactly one iterable argument.

    >>> list(map_one(lambda x: x**2, range(1, 11)))
    [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
    >>> next(map_one(lambda x: x**2, range(0)))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> list(map_one(len, ['foobar', (10, 20), range(1000)]))
    [6, 2, 1000]
    >>> list(map_one(lambda x: x + 1, (x**2 for x in range(1, 6))))
    [2, 5, 10, 17, 26]
    """
    return (func(value) for value in iterable)


def my_filter(predicate, iterable):
    """
    Return an iterator of the values in an iterable that satisfy the predicate.

    If None is passed instead of func, the iterator will yield truthy values.

    This is the same behavior as the builtin filter.

    >>> next(my_filter(lambda n: n < 0, (0, 1, 2)))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> list(my_filter(lambda x: len(x) == 3, ['ham', 'spam', 'foo', 'eggs']))
    ['ham', 'foo']
    >>> list(my_filter(None, (a[1:] for a in ('p', 'xy', [3], (1, 2, 3), 'c'))))
    ['y', (2, 3)]
    """
    if predicate is None:
        predicate = lambda x: x
    return (value for value in iterable if predicate(value))


def distinct_simple(iterable):
    """
    Yield only first occurrences of equal items.

    It is permitted to assume all values of the input iterable are hashable.

    >>> next(distinct_simple([]))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> list(distinct_simple({3}))
    [3]
    >>> list(distinct_simple(('foo', 'foo')))
    ['foo']
    >>> list(distinct_simple(x**2 for x in range(-3, 6)))
    [9, 4, 1, 0, 16, 25]
    >>> it = distinct_simple([2, 1, 2, 4, 1, 7] * 100_000)
    >>> next(it)
    2
    >>> list(it)
    [1, 4, 7]
    """
    history = set()

    for value in iterable:
        if value not in history:
            history.add(value)
            yield value


def distinct(iterable, *, key=None):
    """
    Yield only first occurrences of values whose associated keys are equal.

    The key parameter is a unary function serving as a key selector. When
    calling this function with a value from the iterable gives the same result
    as calling it with an earlier value from the iterable, don't yield the new
    value.

    The key parameter may also be None instead of a function, in which case
    values in the iterable are considered to be their own keys. Another way of
    saying this is that calling distinct without passing a key selector has the
    same behavior as calling distinct_simple.

    It is permitted to assume the key selector returns only hashable objects,
    and that it is consistent, i.e., when x is y, key(x) == key(y).

    Assume distinct_simple's implementation may change in the future to simply
    forward its argument to distinct (so this shouldn't call distinct_simple).

    >>> next(distinct([]))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> list(distinct({3}))
    [3]
    >>> list(distinct(('foo', 'foo')))
    ['foo']
    >>> list(distinct(x**2 for x in range(-3, 6)))
    [9, 4, 1, 0, 16, 25]
    >>> it = distinct([2, 1, 2, 4, 1, 7] * 100_000)
    >>> next(it)
    2
    >>> list(it)
    [1, 4, 7]

    >>> list(distinct(('foo', 'bar', 'foobar', 'baz', 'quux', 'wq'), key=len))
    ['foo', 'foobar', 'quux', 'wq']
    >>> list(distinct(range(-3, 6), key=lambda x: x**2))
    [-3, -2, -1, 0, 4, 5]
    >>> list(distinct([[1, 2, 3], [1, 3, 2], [1, 2, 3], [2, 1, 3]], key=tuple))
    [[1, 2, 3], [1, 3, 2], [2, 1, 3]]
    >>> middle = [[], []] * 100_000
    >>> list(distinct([3, *middle, 4], key=id))
    [3, [], [], 4]
    """
    if key is None:
        key = lambda x: x

    history = set()

    for value in iterable:
        image = key(value)
        if image not in history:
            history.add(image)
            yield value
