"""Some basic decorators."""


def peek_arg(func):
    """
    Decorator wrapping a unary function and showing calls to it.

    This peeks at the argument passed when the function is called.
    It does not show the value returned.

    >>> @peek_arg
    ... def square(n): return n**2
    >>> result = square(3)
    square(3)
    >>> result
    9
    >>> @peek_arg
    ... def hello(name): print(f'Hello, {name}!')
    >>> hello('Bob')
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
    ... def square(x): return x**2
    >>> result = square(3)
    square(3) -> 9
    >>> result
    9
    >>> @peek_return
    ... def hello(name): print(f'Hello, {name}!')
    >>> hello('Bob')
    Hello, Bob!
    hello('Bob') -> None
    """
    def wrapper(arg):
        result = func(arg)
        print(f'{func.__name__}({arg!r}) -> {result}')
        return result

    return wrapper


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


def thrice(func):
    """
    Decorator to repeat a parameterless function three times (with no return).

    >>> @thrice
    ... def hello(): print('Hello, world!')
    >>> hello()
    Hello, world!
    Hello, world!
    Hello, world!
    >>> @thrice
    ... def answer(): return 42
    >>> answer()  # No output; the wrapped function always returns None.
    >>>
    """
    def wrapper():
        for _ in range(3):
            func()

    return wrapper


def repeat(count):
    """
    Parameterized decorator to repeat a function a given number of times.

    >>> @repeat(2)
    ... def bye():
    ...     print('Cya later!')
    >>> bye()
    Cya later!
    Cya later!
    """