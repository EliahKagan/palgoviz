#!/usr/bin/env python

"""Hello world example."""

_FORMATS = {
    'en': 'Hello, {}!',
    'es': '¡Hola, {}!',
}


def make_greeter(lang):
    """
    Make a function that greets by name in the language specified by lang.

    >>> greet = make_greeter('es')
    >>> greet.lang
    'es'
    >>> greet('David')
    ¡Hola, David!
    >>> greet('Eliah')
    ¡Hola, Eliah!
    >>> greet.lang = 'en'
    >>> greet('David')
    Hello, David!
    >>> make_greeter('en')('Stalin')  # But we greet Stalin in English???
    Hello, Stalin!
    >>> greet = make_greeter('zx')
    Traceback (most recent call last):
      ...
    ValueError: zx is an unrecognized language code.
    >>> greet.lang = 'qx'
    >>> greet('Churchill')
    Traceback (most recent call last):
      ...
    ValueError: qx is an unrecognized language code.
    """
    if lang not in _FORMATS:
        raise ValueError(f'{lang} is an unrecognized language code.')

    def greeter(name):
        try:
            print(_FORMATS[greeter.lang].format(name))
        except KeyError as error:
            message = f'{greeter.lang} is an unrecognized language code.'
            raise ValueError(message) from error

    greeter.lang = lang

    return greeter


def hello(name, lang='en'):
    """
    Greet the user.

    >>> hello('Eliah')
    Hello, Eliah!
    >>> hello('Eliah','en')
    Hello, Eliah!
    >>> hello('Eliah','es')
    ¡Hola, Eliah!
    >>> hello('Eliah','el')
    Traceback (most recent call last):
      ...
    ValueError: el is an unrecognized language code.
    """
    greeter = make_greeter(lang)
    greeter(name)


def run():
    """Run the doctests."""
    import doctest
    doctest.testmod()


if __name__ == '__main__':  # If we are running this module as a script.
    run()
