"""Some basic decorators."""


def peek_arg(func):
    """
    Decorator wrapping a unary function and showing calls to it.

    This peeks at the argument passed when the function is called.
    It does not show the value returned.

    FIXME: Change this to use the decorator notation.

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


def peek_return(func):
    """
    Decorator wrapping a unary function and showing its return values.

    This peeks at the value returned by the function. It does not print
    anything at the time the function is called.

    >>> @peek_return
    ... def square(x):
    ...     return x**2
    >>> result = square(3)
    square(3) -> 9
    >>> result
    9
    """


def call(func):
    """
    Decorator to call a parameterless function immediately.

    >>> @call
    ... def hi():
    ...     print('Hi, world!')
    Hi, world!
    >>> hi()
    Hi, world!
    """
    func()
    return func
