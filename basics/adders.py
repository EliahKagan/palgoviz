"""Callables that add a fixed value to their argument."""

# FIXME: Write unittest tests for the make_adder function and the Adder class,
# in a separate test module. They should (at least) test all the behaviors
# shown in the doctests. This can be done before or after implementing the
# Adder class. The names (and number) of test classes given in review-notes.txt
# are just suggestions. If your initial tests duplicate logic, such as to test
# behavior that applies to both make_adder and Adder, then reorganize the tests
# to eliminate that duplication. (Once that's done, remove this whole comment.)


def make_adder(left_addend):
    """
    Create a function that adds its argument to the already-given addend.

    >>> f = make_adder(7)
    >>> f(4)
    11
    >>> f(10)
    17
    >>> make_adder(6)(2)
    8
    >>> s = make_adder('cat')
    >>> s(' dog')
    'cat dog'
    """
    def adder(right_addend):
        return left_addend + right_addend
    return adder


class Adder:
    """
    Callable object that adds its argument to the addend given on construction.

    The fixed added an Adder stores and uses is a left addend, which matters in
    some noncommutative meanings of "+", such as sequence concatenation. This
    is the class version of make_adder, with some more features classes allow.

    >>> a = Adder(7)
    >>> a(4)
    11
    >>> a(10)
    17
    >>> Adder(6)(2)
    8
    >>> Adder('cat')
    Adder('cat')
    >>> _(' dog')
    'cat dog'
    >>> {Adder(7), Adder(7), Adder(6), Adder(7.0)} == {Adder(6), Adder(7)}
    True
    >>> a.left_addend
    7
    >>> a.left_addend = 8
    Traceback (most recent call last):
      ...
    AttributeError: can't set attribute 'left_addend'
    >>> a.right_addend = 5  # This would be a conceptual mistake.
    Traceback (most recent call last):
      ...
    AttributeError: 'Adder' object has no attribute 'right_addend'
    """
    # FIXME: Implement this.


if __name__ == '__main__':
    import doctest
    doctest.testmod()
