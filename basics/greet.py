#!/usr/bin/env python

"""Hello world example."""

_FORMATS = {
    'en': 'Hello, {}!',
    'es': '¡Hola, {}!',
}


class Greeter:
    """
    Callable object that greets people by name in a specified language.

    >>> g = Greeter('en')
    >>> g.lung = 'es'
    Traceback (most recent call last):
      ...
    AttributeError: 'Greeter' object has no attribute 'lung'
    """

    __slots__ = ('_lang',)

    def __init__(self, lang):
        """Create a greeter from the language code."""
        self.lang = lang

    def __call__(self, name):
        """Greet a person by name."""
        print(_FORMATS[self._lang].format(name))

    def __eq__(self, other):
        """
        Two Greeter of the same lang should evalulate as equal
        >>> a = Greeter('en')
        >>> b = Greeter('es')
        >>> c = Greeter('en')
        >>> a == b
        False
        >>> a == c
        True
        """
        if self.lang == other.lang:
            return True
        return False


    @property
    def lang(self):
        """The language this Greeter will greet in."""
        return self._lang

    @lang.setter
    def lang(self, value):
        if value not in _FORMATS:
            raise ValueError(f'{value} is an unrecognized language code.')
        self._lang = value


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
    Traceback (most recent call last):
      ...
    ValueError: qx is an unrecognized language code.
    """
    return Greeter(lang)


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
