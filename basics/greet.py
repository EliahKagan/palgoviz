#!/usr/bin/env python

"""Hello world example."""

__all__ = [
    'MutableGreeter',
    'FrozenGreeter',
    'EnumGreeter',
    'make_greeter',
    'hello',
    'run',
]

import enum

_FORMATS = {
    'en': 'Hello, {}!',
    'es': '¡Hola, {}!',
}


# TODO: Extract shared parts of MutableGreeter and FrozenGreeter to an abstract
#       base class, which might be called AbstractGreeter, or just Greeter.


class MutableGreeter:
    """
    Callable object to greet people by name in a specified language. Mutable.

    >>> g = MutableGreeter('en')
    >>> g.lung = 'es'
    Traceback (most recent call last):
      ...
    AttributeError: 'MutableGreeter' object has no attribute 'lung'
    """

    __slots__ = ('_lang',)

    @staticmethod
    def get_known_langs():
        """
        Get known language codes.

        >>> MutableGreeter.get_known_langs()
        ('en', 'es')
        >>> MutableGreeter('es').get_known_langs()
        ('en', 'es')
        """
        return tuple(_FORMATS)

    @classmethod
    def from_greeter(cls, greeter):
        """
        Construct a MutableGreeter from a greeter.

        >>> f = FrozenGreeter('en')
        >>> m = MutableGreeter.from_greeter(f)
        >>> m('World')
        Hello, World!
        """
        return cls(greeter.lang)

    def __init__(self, lang):
        """
        Create a MutableGreeter from the language code.

        >>> MutableGreeter('qx')
        Traceback (most recent call last):
          ...
        ValueError: qx is an unrecognized language code.
        """
        self.lang = lang

    def __call__(self, name):
        """
        Greet a person by name.

        >>> g = MutableGreeter('es')
        >>> g('David')
        ¡Hola, David!
        >>> g.lang = 'en'
        >>> g('Eliah')
        Hello, Eliah!
        """
        print(_FORMATS[self.lang].format(name))

    def __eq__(self, other):
        """
        Check if two MutableGreeters greet in the same language.

        >>> MutableGreeter('en') == MutableGreeter('en')
        True
        >>> MutableGreeter('en') == MutableGreeter('es')
        False
        >>> MutableGreeter('en') == 1
        False
        """
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.lang == other.lang

    def __repr__(self):
        """
        Representation of this MutableGreeter as Python code.

        >>> MutableGreeter('en')
        MutableGreeter('en')
        >>> class MyMutableGreeter(MutableGreeter): pass
        >>> MyMutableGreeter('en')
        MyMutableGreeter('en')
        """
        return f"{type(self).__name__}({self.lang!r})"

    @property
    def lang(self):
        """
        The language this MutableGreeter will greet in.

        >>> g = MutableGreeter('en')
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
    Callable object to greet people by name in a specified language. Immutable.

    >>> g = FrozenGreeter('en')
    >>> g.lung = 'es'
    Traceback (most recent call last):
      ...
    AttributeError: 'FrozenGreeter' object has no attribute 'lung'
    """

    __slots__ = ('_lang',)

    @staticmethod
    def get_known_langs():
        """
        Get known language codes.

        >>> FrozenGreeter.get_known_langs()
        ('en', 'es')
        >>> FrozenGreeter('es').get_known_langs()
        ('en', 'es')
        """
        return tuple(_FORMATS)

    @classmethod
    def from_greeter(cls, greeter):
        """
        Construct a FrozenGreeter from a greeter.

        >>> m = MutableGreeter('en')
        >>> f = FrozenGreeter.from_greeter(m)
        >>> f('World')
        Hello, World!
        """
        return cls(greeter.lang)

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
        print(_FORMATS[self.lang].format(name))

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


# FIXME: Make a subclass of EnumMeta, which could be called _EnumGreeterMeta,
# that overrides __call__ to give an error message of the same style other
# greeters give, when an unrecognized language code is passed. Specify it as
# the metaclass for EnumGreeter. Syntactically, a class's metaclass is
# specified by putting what looks like a "metaclass" keyword argument in the
# list of direct base classes (where the positional arguments, if any, are the
# direct base classes, listed as usual: positionally). The metaclass is the
# only new class that needs to be created for this, and it need not define
# anything other than __call__.
#
# This is a straightforward and blessedly simple use of metaclasses. The goal
# is to facilitate conceptual familiarity with metaclasses, and with their
# significance in enumerations. In a full presentation of metaclasses, it would
# be important to look at documentation. But this is intentionally the smallest
# of toe-dips into the topic. There are no restrictions on what resources, if
# any, you use. But if you are even slightly tempted to look at documentation
# about metaclasses, that suggests you may be going far beyond the intent of
# this sub-exercise. Probably you won't need to look at the documentation on
# enumerations either. Every line of code in the metaclass should be short and
# simple, and the whole metaclass should take no more than 15 lines, including
# blank lines. Probably you will write far less code than that.
#
# FIXME: Raise AttributeError if an attempt is made to assign to a nonexistent
# attribute on an EnumGreeter instance.
#
@enum.unique
class EnumGreeter(enum.Enum):
    """
    Callable Enum to greet people by name in a specified language.

    Enumerators of this class specify available languages. Currently only
    English and Spanish are supported. They are not updated automatically along
    with other greeters in this module.

    >>> EnumGreeter('qx')
    Traceback (most recent call last):
        ...
    ValueError: qx is an unrecognized language code.

    >>> g = EnumGreeter('en')
    >>> g.lung = 'es'
    Traceback (most recent call last):
      ...
    AttributeError: 'EnumGreeter' object has no attribute 'lung'
    """

    ENGLISH = 'en'
    SPANISH = 'es'

    @classmethod
    def get_known_langs(cls):
        """
        Get known language codes.

        >>> EnumGreeter.get_known_langs()
        ('en', 'es')
        >>> EnumGreeter('es').get_known_langs()
        ('en', 'es')
        """
        return tuple(greeter.value for greeter in cls.__members__.values())

    @classmethod
    def from_greeter(cls, greeter):
        """
        Construct an EnumGreeter from a greeter.

        >>> m = MutableGreeter('en')
        >>> e = EnumGreeter.from_greeter(m)
        >>> e('World')
        Hello, World!
        """
        return cls(greeter.lang)

    def __repr__(self):
        """
        Representation as Python code.

        >>> EnumGreeter('en')
        EnumGreeter('en')
        >>> EnumGreeter('es')
        EnumGreeter('es')
        """
        return f'{type(self).__name__}({self.value!r})'

    def __call__(self, name):
        """
        Greet a person by name.

        >>> g = EnumGreeter.SPANISH
        >>> g('David')
        ¡Hola, David!

        >>> e = EnumGreeter.ENGLISH
        >>> e('David')
        Hello, David!
        """
        print(_FORMATS[self.lang].format(name))

    @property
    def lang(self):
        """
        The language this EnumGreeter will greet in.

        >>> e = EnumGreeter('en')
        >>> e.lang
        'en'
        >>> e.lang = 'es'
        Traceback (most recent call last):
          ...
        AttributeError: can't set attribute 'lang'
        """
        return self.value


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
    return MutableGreeter(lang)


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
