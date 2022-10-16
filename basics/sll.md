# `sll.HashNode` subtleties

## Solution to the problem of heterogeneous cycles

In many uses, client code can ensure no heterogeneous cycle forms. But that's
not always feasible. Furthermore, the whole point of cyclic garbage collection
is that even arbitrary cycles do not cause leaks. So it would be good if the
node type could avoid keeping strong references to any heterogeneous cycles no
longer reachable except through its private table.

Nodes hold strong references to their elements and successors. A node's element
and successor thus exist as long as the node. Since the table entry for a node
goes away when the node is collected, it seems the table's references to the
element and successor could be weak instead of strong. Maybe this would work:

```python
cls._table[weakref.ref(value), weakref.ref(next_node)] = node
```

The key there is a tuple of two weak references. Tuples use structural equality
comparison. So the weak references to `value` and `next_node` participate in
calls to `__eq__` and `__hash__` on the key, when it is looked up in the table.

We must attend to several issues, to determine if *any* approach like this
could be correct and, if so, whether the simple approach of using a tuple of
the weak references is sufficient:

1. When a attempt to construct a node should create a new node, will a false
   positive match to an existing entry in the table always be avoided?

2. When an attempt to construct a node should return an existing node instead
   of making a new one, will the existing node actually be found in the table?

3. When a node becomes unreachable and is removed from the table, what happens?
   Do we need to worry about the deletion operation, behind the scenes, looking
   up the key by calling `__hash__` and `__eq__` on *dead* weak references?

4. Is it a problem that not all objects in Python are weak-referenceable?

The first three issues relate to how `weakref.ref` objects behave under
equality comparison. But first...

### Why not just use `weakref.proxy` instead of `weakref.ref`?

The table key for a node holds weak references to its element and successor.
When they are still alive, we want them to contribute to the key's hashing and
equality comparison behavior the same as if they were actually elements of the
key--that is, as if the key held strong references to them. This raises the
question of whether we should use weakref *proxies* instead.

The answer is no. Weak reference proxies [are not
hashable](https://docs.python.org/3/library/weakref.html#weakref.proxy):

> Proxy objects are not
> [hashable](https://docs.python.org/3/glossary.html#term-hashable) regardless
> of the referent; this avoids a number of problems related to their
> fundamentally mutable nature, and prevent their use as dictionary keys.

### Weak reference equality comparison semantics

[The `weakref.ref`
documentation](https://docs.python.org/3/library/weakref.html#weakref.ref)
explains how `__eq__` and `__hash__` work on `weakref.ref` objects.

#### Equality

`weakref.ref` objects are equal if *(1)* they reference the same object, even
if that object has been collected, or *(2)* they reference different objects,
both of which are still alive, that are equal to each other. Otherwise they are
unequal.

> Weak references support tests for equality, but not ordering. If the
> referents are still alive, two references have the same equality relationship
> as their referents (regardless of the *callback*). If either referent has
> been deleted, the references are equal only if the reference objects are the
> same object.

#### Hashing

`weakref.ref` object hash based on their referents (the objects they refer to).

> Weak references are
> [hashable](https://docs.python.org/3/glossary.html#term-hashable) if the
> *object* is hashable. They will maintain their hash value even after the
> *object* was deleted. If
> [`hash()`](https://docs.python.org/3/library/functions.html#hash) is called
> the first time only after the object was deleted, the call will raise
> [`TypeError`](https://docs.python.org/3/library/exceptions.html#TypeError).

Calling `hash` on a `weakref.ref` for the first time raises `TypeError` if its
referent has already been collected. Otherwise, the its hash code is based on
the referent's hash code (so it is consistent with equality comparison), and
the weak reference also caches the hash code, never calling `hash` on the
referent more than once. Even after the referent is collected, calling `hash`
on the weak reference returns the same hash code.

### Issue 1: False positives

*When a attempt to construct a node should create a new node, will a false
positive match to an existing entry in the table always be avoided?*

To subscript the table, a key is constructed, holding weak references to
`value` and `next_node`. This key may, in the worst case, have to be compared
to every key in the table. Can it match a key it shouldn't?

#### Different `value`,

---

Is this really okay? In an entry that maps a key `(value, next_node)` to a
value `node`, is it safe for the key's references to `value` and `next_node` to
be weak references?

It would be easy to say yes, *if* the callback the table registers to remove
the entry were guaranteed to remove it without looking up the entry by key. But
`weakref.WeakValueTable` makes no such promise. Furthermore, its implementation
in CPython stores entries in an underlying dict to satisfy its atomicity
guarantees, and *always* subscripts that dict with the key to remove it.
Subscripting the dict calls `hash` on the key, and also compares it for
equality to one or more keys stored in the dict.

<!-- FIXME: Finish writing the text from here to the HTML comment below. -->
Might it *still* be safe? We have a very nice invariant on our side:
...
So we must reason about the hashing and equality comparison behavior of keys,
whose hashing and equality comparison behavior must delegate to the objects
they hold weak references to, ...
<!-- ^^^^^^ Finish writing the text from the above HTML comment to here. -->

Now there is one more problem: not all objects in Python can be referred to by
weak references! It would be bad only to support weak-referenceable element
types. (For example, we couldn't even store `int` values.) `HashNode` instances
have already been made weak-referenceable, or we wouldn't be able to use them
as values in a `WeakValueDictionary` in the first place. But elements are
allowed to be any hashable immutable objects.

For this, we can make and use weak-referenceable wrappers that stand in front
of the elements. Instead of holding a weak reference to an element, a key in
the table can hold a weak reference to a wrapper object that holds a strong
reference to the element. Of course, with only a weak reference to it, the
wrapper would be immediately eligible for collection. So, likewise, instead of
holding a strong reference to its element, a node can hold a strong reference
to the wrapper object that holds a strong reference to the element. Then both
the element and the wrapper are guaranteed to exist as long as the node needs
them, but to be eligible for collection once they can only be reached from the
table.

To avoid making other code much more complicated, the the class of the wrappers
should cause them to delegate equality comparison and hashing to the element,
and should allow the element to be accessed, since the `sll.HashNode.value`
property will access the element through the wrapper. I called my wrapper class
`_Box`. (These wrappers should *not* be confused with weakref proxy objects,
which are unrelated, and also not likely to be useful anywhere in the code of
`sll.HashNode` or its helpers, since they are not hashable.)
