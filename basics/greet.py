#!/usr/bin/env python

"""Hello world example."""

FORMATS = {
    'en': 'Hello, {}!',
    'es': '¡Hola, {}!',
}


def make_greeter(lang):
    """
    Make a function that greets by name in the language specified by lang.

    >>> greet = make_greeter('es')
    >>> greet('David')
    ¡Hola, David!
    >>> greet('Eliah')
    ¡Hola, Eliah!
    >>> make_greeter('en')('Stalin')  # But we greet Stalin in English???
    Hello, Stalin!
    >>> greet = make_greeter('zx')
    Traceback (most recent call last):
      ...
    ValueError: zx is an unrecognized language code.
    """
    try:
        lang_format = FORMATS[lang]
    except KeyError as error:
        raise ValueError(f'{lang} is an unrecognized language code.') from error

    def greeter(name):
        print(lang_format.format(name))

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
