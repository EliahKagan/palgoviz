"""
Reproduction of the structure of the collections.abc inheritance hierarchy.

This submodule contains stubs corresponding to each public class defined in the
collections.abc standard library module. They have no methods, but they
reproduce all inheritance details from the _collections_abc.py implementation
in CPython 3.10. This includes the order in which base classes are listed,
which is not documented and could potentially vary across even minor versions
of CPython or between CPython and another Python implementation. Tests of
class_graph functions that use collections.abc may break as a result of an
update; if they do, it should be possible to discern the reason by noticing
that corresponding tests using class_graph.examples.abc_stubs still work.
"""


class Hashable:
    """Stub for collections.abc.Hashable."""

    __slots__ = ()


class Awaitable:
    """Stub for collections.abc.Awaitable."""

    __slots__ = ()


class Coroutine(Awaitable):
    """Stub for collections.abc.Coroutine."""

    __slots__ = ()


class AsyncIterable:
    """Stub for collections.abc.AsyncIterable."""

    __slots__ = ()


class AsyncIterator(AsyncIterable):
    """Stub for collections.abc.AsyncIterator."""

    __slots__ = ()


class AsyncGenerator(AsyncIterator):
    """Stub for collections.abc.AsyncGenerator."""

    __slots__ = ()


class Iterable:
    """Stub for collections.abc.Iterable."""

    __slots__ = ()


class Iterator(Iterable):
    """Stub for collections.abc.Iterator."""

    __slots__ = ()


class Reversible(Iterable):
    """Stub for collections.abc.Reversible."""

    __slots__ = ()


class Generator(Iterator):
    """Stub for collections.abc.Generator."""

    __slots__ = ()


class Sized:
    """Stub for collections.abc.Sized."""

    __slots__ = ()


class Container:
    """Stub for collections.abc.Container."""

    __slots__ = ()


class Collection(Sized, Iterable, Container):
    """Stub for collections.abc.Collection."""

    __slots__ = ()


class Callable:
    """Stub for collections.abc.Callable."""

    __slots__ = ()


class Set(Collection):
    """Stub for collections.abc.Set."""

    __slots__ = ()


class MutableSet(Set):
    """Stub for collections.abc.MutableSet."""

    __slots__ = ()


class Mapping(Collection):
    """Stub for collections.abc.Mapping."""

    __slots__ = ()


class MappingView(Sized):
    """Stub for collections.abc.MappingView."""

    __slots__ = ()


class KeysView(MappingView, Set):
    """Stub for collections.abc.KeysView."""

    __slots__ = ()


class ItemsView(MappingView, Set):
    """Stub for collections.abc.ItemsView."""

    __slots__ = ()


class ValuesView(MappingView, Collection):
    """Stub for collections.abc.ValuesView."""

    __slots__ = ()


class MutableMapping(Mapping):
    """Stub for collections.abc.MutableMapping."""

    __slots__ = ()


class Sequence(Reversible, Collection):
    """Stub for collections.abc.Sequence."""

    __slots__ = ()


class ByteString(Sequence):
    """Stub for collections.abc.ByteString."""

    __slots__ = ()


class MutableSequence(Sequence):
    """Stub for collections.abc.MutableSequence."""

    __slots__ = ()
