"""Demonstration of simple decorated function."""

from decorators import peek_arg, call


@peek_arg
def greet(name):
    """
    Greet a user, printing information about the call.

    >>> greet('Bob')
    Hello, Bob! Do you like decorators?
    """
    print(f'Hello, {name}! Do you like decorators?')


@call
def hello():
    """
    Print Hello world

    >>> hello()
    Hello, World!
    """
    print('Hello, World!')
