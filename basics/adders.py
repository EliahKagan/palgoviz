"""Making functions that add to the same value."""


def make_adder(addend):
    """
    Create a function that adds its argument to the already-given addend.

    >>> f = make_adder(7)
    >>> f(4)
    11
    >>> f(10)
    17
    >>> make_adder(6)(2)
    8
    """
    def adder(input):
        return addend + input
    return adder


if __name__ == '__main__':
    import doctest
    doctest.testmod()
