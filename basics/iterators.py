#!/usr/bin/env python

"""
Concepts for iterators, revisited.

This module could theoretically be used to introduce the fundamentals of
iterators and generators, but it is NOT meant for that. Explanations target
readers who already know what generator functions, generator objects, and
iterators are. These are reviewed at a fast pace, without definitions, using
facilities from the inspect and collections.abc modules novices may not know.

Besides review, the primary purpose of this module is to present the __iter__
and __next__ special methods that the iter and next builtins use behind the
scenes. This reveals the nature of generator objects as state machines. That,
in turn, shows why attempts to construct some kinds of iterable objects can
reasonably return an existing object, but attempts to construct iterators
(including generator objects) must always† return a newly created object.

On generators, see also the modules gencomp1.py and gencomp2.py, and the
notebooks gencomp1.ipynb, gencomp2.ipynb, and gencomp3.ipynb. Some techniques
appear in functions.py. On customizing object construction, see classes3.ipynb.

† Arguably there is one exception: [FIXME: what?], because [FIXME: why?].
"""

# Several imports are just for doctests. We don't usually do this, but it seems
# to improve clarity in this module. (We suppress flake8's "unused" warning.)
from collections.abc import Iterable, Iterator  # noqa: F401
import enum
from inspect import (  # noqa: F401
    getgeneratorstate,
    isclass,
    isfunction,
    isgenerator,
    isgeneratorfunction,
)
import itertools  # noqa: F401


def gen_rgb():
    """
    Yield the words "red", "green", and "blue", in that order.

    No other iterator is used. So while ``yield from ('red', 'green', 'blue')``
    is a reasonable way to do this, nothing like that is done here.

    A generator function is a factory for generator objects. A generator object
    itself is an iterator (it is also called a "generator iterator"). The
    factory is not itself an iterator, nor is it otherwise iterable.

    >>> isfunction(gen_rgb), isgeneratorfunction(gen_rgb), isgenerator(gen_rgb)
    (True, True, False)
    >>> isinstance(gen_rgb, Iterable), isinstance(gen_rgb, Iterator)
    (False, False)

    >>> list(gen_rgb)
    Traceback (most recent call last):
      ...
    TypeError: 'function' object is not iterable

    Calling it returns a generator object, which is an iterator, thus iterable:

    >>> it = gen_rgb()
    >>> isfunction(it), isgeneratorfunction(it), isgenerator(it)
    (False, False, True)
    >>> isinstance(it, Iterable), isinstance(it, Iterator)
    (True, True)

    >>> list(it)
    ['red', 'green', 'blue']

    Iterators are exhausted by iteration:

    >>> list(it)
    []

    Calling iter on an iterator gives an equivalent iterator, which should
    always be (and is, technically, required to be) the same iterator object:

    >>> it = gen_rgb()
    >>> iter(it) is it
    True

    Since iterators are exhausted by iteration, calling an iterator factory
    must always return a new iterator object. Equality is reference-based.

    >>> it2 = gen_rgb()
    >>> it is it2, it == it2
    (False, False)

    Each generator object created by a generator function separately executes
    the code in the function body, with its own instruction pointer and local
    variables. Before the first call to next, it has not even entered the code:

    >>> getgeneratorstate(it)
    'GEN_CREATED'

    The first call to next changes its state from GEN_CREATED to GEN_RUNNING,
    but its state is GEN_SUSPENDED after it yields, which is what we see:

    >>> next(it), getgeneratorstate(it)
    ('red', 'GEN_SUSPENDED')

    The full state of the generator object has more to it than just what
    inspect.getgeneratorstate returns. It knows where to resume.

    >>> next(it), getgeneratorstate(it), next(it), getgeneratorstate(it)
    ('green', 'GEN_SUSPENDED', 'blue', 'GEN_SUSPENDED')

    If the code returns instead of yielding, StopIteration is raised, and the
    generator state changes to GEN_CLOSE:

    >>> next(it)
    Traceback (most recent call last):
      ...
    StopIteration
    >>> getgeneratorstate(it), list(it), list(it)
    ('GEN_CLOSED', [], [])

    None of this affects it2, because that is a separate generator object:

    >>> getgeneratorstate(it2), next(it2), getgeneratorstate(it2)
    ('GEN_CREATED', 'red', 'GEN_SUSPENDED')

    Unlike most iterators, generator objects have a close method, which takes
    them to the GEN_CLOSED state. This skips over the remaining two elements:

    >>> it2.close()
    >>> getgeneratorstate(it2), list(it2), list(it2)
    ('GEN_CLOSED', [], [])

    Closing a suspended generator object raises GeneratorExit in it, to exit
    context managers and run finally blocks. See gencomp3.ipynb.

    Generator objects do not have instance dictionaries, but they are weakly
    referenceable. This is even though no __slots__ or __weakref__ attributes
    are present. (This is possible as the generator type is implemented in C.)
    """
    yield 'red'
    yield 'green'
    yield 'blue'


class PaletteG:
    """
    Words "red", "green", and "blue". A generator is used.

    This class is a factory for non-iterator iterables. An instance represents
    those three color words, in the same sense that a range represents numbers.

    The PaletteG class is not itself iterable (that would be weird). Instances
    are iterable, but they are not iterators. Their iterators are generator
    objects. This class is self-contained but it uses the same logic as gen_rgb
    above, by implementing a special method as a generator function.

    >>> isinstance(PaletteG, Iterable), isinstance(PaletteG, Iterator)
    (False, False)
    >>> issubclass(PaletteG, Iterable), issubclass(PaletteG, Iterator)
    (True, False)
    >>> isinstance(PaletteG(), Iterable), isinstance(PaletteG(), Iterator)
    (True, False)

    Regarding the above, note that PaletteG does not inherit from anything
    (except object) and is not registered as a virtual subclass of any ABC.

    Unlike generator objects and other iterators, a PaletteG instance is not
    exhausted by iteration. It may be reused freely, even concurrently:

    >>> palette = PaletteG()
    >>> list(palette), list(palette)
    (['red', 'green', 'blue'], ['red', 'green', 'blue'])
    >>> list(zip(palette, palette))
    [('red', 'red'), ('green', 'green'), ('blue', 'blue')]
    >>> list(itertools.chain(palette, palette))
    ['red', 'green', 'blue', 'red', 'green', 'blue']

    Iterators are all independent. Being generator objects, they have generator
    specific features, as well as satisfying all requirements for iterators:

    >>> it, it2 = iter(palette), iter(palette)
    >>> iter(it) is it, it is it2, it == it2
    (True, False, False)
    >>> getgeneratorstate(it), next(it), getgeneratorstate(it), next(it)
    ('GEN_CREATED', 'red', 'GEN_SUSPENDED', 'green')
    >>> getgeneratorstate(it2), next(it2), getgeneratorstate(it2)
    ('GEN_CREATED', 'red', 'GEN_SUSPENDED')

    >>> it.close()
    >>> list(it)
    []
    >>> list(it2)
    ['green', 'blue']

    Iterators hold state. Iterables that are not iterators often do too. For
    example, range(2) is an iterable but not an iterator, and its state differs
    from that of range(3). Those ranges are accordingly unequal. Other examples
    include tuples and lists; their state is their elements. An interesting
    thing about PaletteG instances is that they hold no state. More precisely,
    they have zero information other than their type. It is appropriate for all
    PaletteG instances to be equal to each other. It is reasonable to override
    __eq__ and __hash__ to achieve this. Instead, we make PaletteG a singleton.

    >>> {PaletteG(), PaletteG()}
    {PaletteG()}
    >>> PaletteG() is PaletteG()
    True
    """

    __slots__ = ()

    _instance = None

    def __new__(cls):
        """Get the PaletteG instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self):
        """Python code representation for debugging."""
        return f'{type(self).__name__}()'

    def __iter__(self):
        """Yield the color words."""
        yield 'red'
        yield 'green'
        yield 'blue'


PaletteG()  # Eagerly create the singleton to prevent data races later.


# FIXME: Define a nonpublic enumeration, _State, to represent states that
# a PaletteIterator instance can be in.
@enum.unique
class _State(enum.Enum):
    """State for PaletteIteratorSimple and PaletteIterator."""

    RED = enum.auto()
    GREEN = enum.auto()
    BLUE = enum.auto()
    FINISHED = enum.auto()


class PaletteIterator:
    """
    Custom iterator class for Palette. This can also be used on its own.

    This class is a factory for non-generator iterators. See Palette below;
    calling iter on its instances returns an instance of this class.

    Note that, although attempting to construct a new instance of Palette can
    safely return an existing object--and in fact Palette, like PaletteG, is a
    singleton--it would never be safe for that happen with PaletteIterator. If
    a preexisting PaletteIterator instance were ever returned, then separate
    attempts to iterate through Palette colors would interfere with each other.

    The class is of course not iterable. Instances are, and they are iterators:

    >>> cls = PaletteIterator
    >>> isinstance(cls, Iterable), isinstance(cls, Iterator)
    (False, False)
    >>> issubclass(cls, Iterable), issubclass(cls, Iterator)
    (True, True)
    >>> isinstance(cls(), Iterable), isinstance(cls(), Iterator)
    (True, True)

    These iterators are all independent. But they are not generator objects, so
    their state cannot be inspected by inspect.getgeneratorstate. Non-generator
    iterators do not usually supply close methods, but it is sometimes useful
    for them to have such a method, and this class implements such a method.

    Note that the presence of a close method is not part of what it means to be
    an iterator. Nor does this class implement all other parts of the protocol
    generators use. (Generators have send and throw methods, which this project
    does not currently cover, and which wouldn't be useful in PaletteIterator.)

    >>> it, it2 = PaletteIterator(), PaletteIterator()
    >>> iter(it) is it, it is it2, it == it2
    (True, False, False)
    >>> next(it), next(it)
    ('red', 'green')
    >>> next(it2)
    'red'

    >>> it.close()
    >>> list(it)
    []
    >>> list(it2)
    ['green', 'blue']

    Iterators can have instance dictionaries, but it usually makes sense to
    omit them for performance (iterators are used heavily in loops). It may not
    be necessary to support weak references. Most non-generator iterators in
    the standard library (e.g., zip, itertools.count) don't. To show how that
    feature of generator objects can be achieved, PaletteIterator allows them.

    >>> hasattr(it, '__dict__')
    False
    >>> import weakref; weakref.ref(it)  # doctest: +ELLIPSIS
    <weakref at 0x...; to 'PaletteIterator' at 0x...>
    """

    __slots__ = ('_state', '__weakref__')

    def __init__(self):
        """Create a new iterator, associated with the PaletteS instance."""
        self._state = _State.RED

    def __repr__(self):
        """Representation for debugging. Not runnable as code."""
        typename = type(self).__name__
        return f'<{typename} at 0x{id(self):X}, state={self._state!r}>'

    def __iter__(self):
        """Return the same object, since this is an iterator."""
        return self

    def __next__(self):
        """Get the next color word, or raise StopIteration if exhausted."""
        match self._state:
            case _State.RED:
                self._state = _State.GREEN
                return 'red'
            case _State.GREEN:
                self._state = _State.BLUE
                return 'green'
            case _State.BLUE:
                self._state = _State.FINISHED
                return 'blue'
            case _State.FINISHED:
                raise StopIteration

        raise AssertionError(f'invalid state {self._state!r}')

    def close(self):
        """Close this iterator, so it does not yield any more color words."""
        self._state = _State.FINISHED


class Palette:
    """
    Words "red", "green", and "blue". No generator is used.

    This is like PaletteG, but calling iter on an instance returns an iterator
    that is not a generator object, but is instead a PaletteIterator instance.

    >>> isinstance(Palette, Iterable), isinstance(Palette, Iterator)
    (False, False)
    >>> issubclass(Palette, Iterable), issubclass(Palette, Iterator)
    (True, False)
    >>> isinstance(Palette(), Iterable), isinstance(Palette(), Iterator)
    (True, False)

    >>> palette = Palette()
    >>> list(palette), list(palette)
    (['red', 'green', 'blue'], ['red', 'green', 'blue'])
    >>> list(zip(palette, palette))
    [('red', 'red'), ('green', 'green'), ('blue', 'blue')]
    >>> list(itertools.chain(palette, palette))
    ['red', 'green', 'blue', 'red', 'green', 'blue']

    >>> iter(palette)  # FIXME: Fill in the second "...".  # doctest: +ELLIPSIS
    <PaletteIterator at 0x..., state=...>
    >>> next(_), _     # FIXME: Here, too. (It changed.)   # doctest: +ELLIPSIS
    ('red', <PaletteIterator at 0x..., state=...>)

    >>> {Palette(), Palette()}
    {Palette()}
    >>> Palette() is Palette()
    True
    >>> Palette() is PaletteG()  # That would be bad.
    False
    """

    __slots__ = ()

    _instance = None

    def __new__(cls):
        """Get the Palette instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self):
        """Python code representation for debugging."""
        return f'{type(self).__name__}()'

    def __iter__(self):
        """Yield the color words."""
        return PaletteIterator()


Palette()  # Eagerly create the singleton to prevent data races later.


__all__ = [thing.__name__ for thing in (
    gen_rgb,
    PaletteG,
    PaletteIterator,
    Palette,
)]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
