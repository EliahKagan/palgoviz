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

    wrapper.__name__ = func.__name__
    wrapper.__module__ = func.__module__
    wrapper.__qualname__ = func.__qualname__
    wrapper.__doc__ = func.__doc__
    wrapper.__annotations__ = func.__annotations__

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
    @give_metadata_from(func)
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
    def decorator(func):
        def wrapper():
            for _ in range(count):
                func()

        return wrapper

    return decorator


def give_metadata_from(wrapped):
    """Parameterized decorater to give a functions metadata to a wrapper."""
    def decorator(wrapper):
        wrapper.__name__ = wrapped.__name__
        wrapper.__module__ = wrapped.__module__
        wrapper.__qualname__ = wrapped.__qualname__
        wrapper.__doc__ = wrapped.__doc__
        wrapper.__annotations__ = wrapped.__annotations__
        return wrapper

    return decorator


# TODO: Cover the differences between these two functions:


def does_nothing(func):
    # mywrapper has the same behavior as func when called with 1 argument.
    # But they are not the same function.
    def mywrapper(arg):
        return func(arg)
    return mywrapper


def does_nothing_2(func):
    # This returns func itself.
    return func
