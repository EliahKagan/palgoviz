#!/usr/bin/env python

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

"""Hello world examples."""

__all__ = [
    'MutableGreeter',
    'FrozenGreeter',
    'EnumGreeter',
    'UniqueGreeter',
    'make_greeter',
    'hello',
    'run',
]

import enum
import threading
import weakref

_FORMATS = {
    'en': 'Hello, {}!',
    'es': '¡Hola, {}!',
}

# FIXME: After all four greeter classes pass their doctests, and any other
# reorganization of the doctests is done, give each class doctests for
# positional class patterns in match-case, then get them to pass.

# TODO: After writing unittest tests, extract shared parts of MutableGreeter
# and FrozenGreeter, and maybe EnumGreeter and UniqueGreeter, to an abstract
# base class. This ABC could be called AbstractGreeter, or just Greeter.


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
        AttributeError: property 'lang' of 'FrozenGreeter' object has no setter
        """
        return self._lang


class _EnumGreeterMeta(enum.EnumMeta):
    """Metaclass to customize unrecognized language errors for EnumGreeter."""

    def __call__(self, lang):
        try:
            return super().__call__(lang)
        except ValueError as error:
            message = f'{lang} is an unrecognized language code.'
            raise ValueError(message) from error


@enum.unique
class EnumGreeter(enum.Enum, metaclass=_EnumGreeterMeta):
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

    def __setattr__(self, name, value):
        """Creation of new public attributes is suppressed."""
        if not name.startswith('_') and name != 'lang':
            raise AttributeError(
                f'{type(self).__name__!r} object has no attribute {name!r}')

        super().__setattr__(name, value)

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
        AttributeError: property 'lang' of 'EnumGreeter' object has no setter
        """
        return self.value


class UniqueGreeter:
    """
    Callable object to greet people by name. Unique per language. Thread-safe.

    More than one instance of UniqueGreeter for the same language may be
    created, but never with overlapping lifetimes. When an instance already
    exists for a language, calling UniqueGreeter with the same language code is
    guaranteed to return the existing instance. But instances' lifetimes are
    not prolonged: the UniqueGreeter class does nothing to prevent any instance
    from being collected when all outside references to it have gone away.

    (Like MutableGreeter/FrozenGreeter, this can use any language in _FORMATS.)

    >>> UniqueGreeter('es')
    UniqueGreeter('es')
    >>> UniqueGreeter('qx')
    Traceback (most recent call last):
        ...
    ValueError: qx is an unrecognized language code.
    >>> UniqueGreeter('en')('Eve')
    Hello, Eve!
    >>> UniqueGreeter('es')('Eve')
    ¡Hola, Eve!
    >>> UniqueGreeter.get_known_langs()
    ('en', 'es')

    >>> UniqueGreeter('en') is UniqueGreeter('en')
    True
    >>> UniqueGreeter('es') is UniqueGreeter('es')
    True
    >>> UniqueGreeter('en') is UniqueGreeter('es')
    False
    >>> UniqueGreeter('en') is UniqueGreeter('english'[:2])
    True
    >>> UniqueGreeter.from_greeter(MutableGreeter('en')) is UniqueGreeter('en')
    True
    >>> UniqueGreeter.from_greeter(MutableGreeter('es')) is UniqueGreeter('es')
    True

    >>> len({UniqueGreeter('en'), UniqueGreeter('es'), UniqueGreeter('en')})
    2
    >>> ug = UniqueGreeter('en')
    >>> ug.lang
    'en'
    >>> ug.lang = 'es'
    Traceback (most recent call last):
        ...
    AttributeError: property 'lang' of 'UniqueGreeter' object has no setter
    >>> ug.lung = 'es'
    Traceback (most recent call last):
      ...
    AttributeError: 'UniqueGreeter' object has no attribute 'lung'

    These tests assume no other code in the process running the doctests has
    created and *kept* references to UniqueGreeter instances:

    >>> from palgoviz.testing import collect_if_not_ref_counting as coll
    >>> coll(); UniqueGreeter.count_instances()
    1
    >>> ug1 = UniqueGreeter('en'); coll(); UniqueGreeter.count_instances()
    1
    >>> ug2 = UniqueGreeter('es'); coll(); UniqueGreeter.count_instances()
    2
    >>> del ug; coll(); UniqueGreeter.count_instances()
    2
    >>> ug1 = ug2; coll(); UniqueGreeter.count_instances()
    1
    >>> del ug1, ug2; coll(); UniqueGreeter.count_instances()
    0

    FIXME: After all doctests pass, move many into method docstrings.
    """

    __slots__ = ('__weakref__', '_lang',)

    _lock = threading.Lock()
    _table = weakref.WeakValueDictionary()

    @staticmethod
    def get_known_langs():
        """Get known language codes."""
        return tuple(_FORMATS)

    @classmethod
    def count_instances(cls):
        """Return the number of currently existing instances."""
        # In CPython, it would be okay to forgo this lock, because CPython's
        # WeakValueDictionary delegates to an underlying dict, and basic dict
        # operations, if they need not call into Python code, are atomic, due
        # to the GIL. It would probably also be okay in any other current or
        # future Python implementation: a WeakValueDictionary may lose items
        # due to a refcount decrement or GC cycle running at any time on any
        # thread, and it seems implausible that any strategy that allows len to
        # be called while that is happening (as it must) would fail to allow it
        # otherwise. Still, this isn't a documented guarantee, count_instances
        # is rarely called (so it can be slow), and locking on len is safe from
        # deadlock. So omitting the lock is, at best, a premature optimization.
        with cls._lock:
            return len(cls._table)

    @classmethod
    def from_greeter(cls, greeter):
        """Create or retrieve the UniqueGreeter from a greeter."""
        return cls(greeter.lang)

    def __new__(cls, lang):
        """Create or retrieve the UniqueGreeter from the language code."""
        if lang not in _FORMATS:
            raise ValueError(f'{lang} is an unrecognized language code.')

        with cls._lock:
            # We *must* use EAFP for this, since the instance could exist when
            # checked, then be collected before being accessed by subscripting.
            try:
                instance = cls._table[lang]
            except KeyError:
                instance = super().__new__(cls)
                instance._lang = lang
                cls._table[lang] = instance

        return instance

    def __repr__(self):
        """Representation of this UniqueGreeter as python code."""
        return f"{type(self).__name__}({self.lang!r})"

    def __call__(self, name):
        """Greet a person by name."""
        print(_FORMATS[self._lang].format(name))

    @property
    def lang(self):
        """The language this UniqueGreeter will greet in."""
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
    """
    Run the doctests.

    This is usually called "main". But unlike in C, that is only a convention.
    Also, when the logic to be done when the module is run as a script is as
    simple as the body of this function, we more often put it directly under
    the "if" check below (rather than in a function). Here, a function is used
    to demonstrate the technique.
    """
    import doctest
    doctest.testmod()


if __name__ == '__main__':  # If we are running this module as a script.
    run()
