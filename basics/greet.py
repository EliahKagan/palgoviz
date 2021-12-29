#!/usr/bin/env python

"""Hello world example."""


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
    match lang:
        case 'en':
            print('Hello, {}!'.format(name))  # .format demonstration
        case 'es':
            print('¡Hola, {}!'.format(name))  # fstring demonstration en español en la manera de "format"
        case _:  
            raise ValueError(f'{lang} is an unrecognized language code.')


def run():
    """Run the doctests."""
    import doctest
    doctest.testmod()


if __name__ == '__main__':  # If we are running this module as a script.
    run()
