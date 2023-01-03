# Copyright (c) 2022 David Vassallo and Eliah Kagan
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

"""Demonstration of simple decorated function."""

__all__ = ['greet', 'hello']

from palgoviz.decorators import call, peek_arg


@peek_arg
def greet(name):
    """
    Greet a user, printing information about the call.

    >>> greet('Bob')
    greet('Bob')
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
