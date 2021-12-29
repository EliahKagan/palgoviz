#!/usr/bin/env python

"""Hello world example."""

FORMATS = {'en': 'Hello, {}!', 'es': '¡Hola, {}!'}


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
    try:
        print(FORMATS[lang].format(name))   # dictionary test   
    except KeyError:
        raise ValueError(f'{lang} is an unrecognized language code.')


def run():
    """Run the doctests."""
    import doctest
    doctest.testmod()


if __name__ == '__main__':  # If we are running this module as a script.
    run()
