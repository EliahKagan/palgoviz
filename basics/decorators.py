"""Some basic decorators."""


def peek_arg(func):
    """
    Return a wrapper for unary function that prints how it is called.

    >>> def square(n): return n**2
    >>> psquare = peek_arg(square)
    >>> result = psquare(3)
    square(3)
    >>> result
    9
    >>> def hello(name): print(f'Hello, {name}!')
    >>> phello = peek_arg(hello)
    >>> phello('Bob')
    hello('Bob')
    Hello, Bob!
    """

    def wrapper(arg):
        print(f'{func.__name__}({arg!r})')
        return func(arg)

    return wrapper

def call(func):
    """Return a wrapper for a function with no arguments that calls the function"""
    def wrapper():
        func()
        return func()
    return wrapper
