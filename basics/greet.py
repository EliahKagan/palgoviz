#!/usr/bin/env python

"""Hello world example."""

_FORMATS = {
    'en': 'Hello, {}!',
    'es': '¡Hola, {}!',
}


# TODO: Extract shared parts of Greeter and FrozenGreeter to an abstract base
#       class.


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
        """
        Create a greeter from the language code.

        >>> Greeter('qx')
        Traceback (most recent call last):
          ...
        ValueError: qx is an unrecognized language code.
        """
        self.lang = lang

    def __call__(self, name):
        """
        Greet a person by name.

        >>> g = Greeter('es')
        >>> g('David')
        ¡Hola, David!
        >>> g.lang = 'en'
        >>> g('Eliah')
        Hello, Eliah!
        """
        print(_FORMATS[self._lang].format(name))

    def __eq__(self, other):
        """
        Check if two Greeters greet in the same language.

        >>> Greeter('en') == Greeter('en')
        True
        >>> Greeter('en') == Greeter('es')
        False
        >>> Greeter('en') == 1
        False
        """
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.lang == other.lang


    def __repr__(self):
        """
        Representation of this Greeter as python code.

        >>> Greeter('en')
        Greeter('en')
        >>> class MyGreeter(Greeter): pass
        >>> MyGreeter('en')
        MyGreeter('en')
        """
        return f"{type(self).__name__}({self.lang!r})"

    @property
    def lang(self):
        """
        The language this Greeter will greet in.

        >>> g = Greeter('en')
        >>> g.lang = 'qx'
        Traceback (most recent call last):
          ...
        ValueError: qx is an unrecognized language code.
        """
        return self._lang

    @lang.setter
    def lang(self, value):
        if value not in _FORMATS:
            raise ValueError(f'{value} is an unrecognized language code.')
        self._lang = value


class FrozenGreeter:
    """
    Callable object that greets people by name in a specified language. Immutable.

    >>> g = FrozenGreeter('en')
    >>> g.lung = 'es'
    Traceback (most recent call last):
      ...
    AttributeError: 'FrozenGreeter' object has no attribute 'lung'
    """

    __slots__ = ('_lang',)

    def __init__(self, lang):
        """
        Create a FrozenGreeter from the language code.

        >>> FrozenGreeter('qx')
        Traceback (most recent call last):
          ...
        ValueError: qx is an unrecognized language code.
        """
        if lang not in _FORMATS:
            raise ValueError(f'{lang} is an unrecognized language code.')
        self._lang = lang

    def __call__(self, name):
        """
        Greet a person by name.

        >>> g = FrozenGreeter('es')
        >>> g('David')
        ¡Hola, David!
        """
        print(_FORMATS[self._lang].format(name))

    def __eq__(self, other):
        """
        Check if two FrozenGreeters greet in the same language.

        >>> FrozenGreeter('en') == FrozenGreeter('en')
        True
        >>> FrozenGreeter('en') == FrozenGreeter('es')
        False
        >>> FrozenGreeter('en') == 1
        False
        """
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.lang == other.lang

    def __hash__(self):
        """
        Hash a FrozenGreeter. If x == y, hash(x) should = hash(y).

        >>> fg1 = FrozenGreeter('en')
        >>> fg2 = FrozenGreeter('en')
        >>> hash(fg1) == hash(fg2)
        True
        """
        return hash(self._lang)

    def __repr__(self):
        """
        Representation of this FrozenGreeter as python code.

        >>> FrozenGreeter('en')
        FrozenGreeter('en')
        >>> class MyFrozenGreeter(FrozenGreeter): pass
        >>> MyFrozenGreeter('en')
        MyFrozenGreeter('en')
        """
        return f"{type(self).__name__}({self.lang!r})"

    @property
    def lang(self):
        """
        The language this FrozenGreeter will greet in.

        >>> fg = FrozenGreeter('en')
        >>> fg.lang = 'es'
        Traceback (most recent call last):
          ...
        AttributeError: can't set attribute 'lang'
        """
        return self._lang


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
