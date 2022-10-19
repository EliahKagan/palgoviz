# `sll.HashNode` subtleties

***WARNING*: This file contains spoilers, if you are implementing anything in
`sll.py` as an exercise!**

## Solution to the problem of heterogeneous cycles

*See `test_sll.TestHashNodeHeterogeneousCycles` for how we are defining this
problem.*

In many uses, client code can ensure no heterogeneous cycle forms. But that's
not always feasible. Furthermore, the whole point of cyclic garbage collection
is that even arbitrary cycles do not cause leaks. So it would be good if the
node type could avoid keeping strong references to any heterogeneous cycles no
longer reachable except through its private table.

Nodes hold strong references to their elements and successors. So a node's
element and successor live at least as long as the node. Since the table entry
for a node goes away when the node is collected, it seems the table's
references to the element and successor could be weak instead of strong. Maybe
this would work:

```python
cls._table[weakref.ref(value), weakref.ref(next_node)] = node
```

The key there is a tuple of two weak references. Tuples use structural equality
comparison. So the weak references to `value` and `next_node` participate in
calls to `__eq__` and `__hash__` on the key, when it is looked up in the table.

We must attend to several issues, to determine if *any* approach like this
could possibly be correct and, if so, whether the simple approach of using a
tuple of the weak references is actually sufficient:

1. When an attempt to construct a node should create a new node, will a false
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
referent has already been collected. Otherwise, its hash code is based on the
referent's hash code (so it is consistent with equality comparison), and the
weak reference also caches the hash code, never calling `hash` on the referent
more than once. Even after the referent is collected, calling `hash` on the
weak reference returns the same hash code.

### Issue 1: False positives

*When an attempt to construct a node should create a new node, will a false
positive match to an existing entry in the table always be avoided?*

To subscript the table, a key is constructed, holding weak references to
`value` and `next_node`. These weak references are live (their targets, at this
point, are local variables of the executing function). This key may, in the
worst case, have to be compared to every key already in the table. Can it
compare equal to a key it shouldn't?

Suppose the new key is compared to a key in the table whose `value` and
`next_node` are both alive. Since all weak references being compared refer to
live objects, the effect is the same as comparing the objects themselves. Thus,
if the new key compares equal to the preexisting key, then the new key's
`value` is equal to the preexisting `value`, and the new key's `next_node` is
the same object as the preexisting `next_node` (since we ensure `next_node` is
always a `HashNode` object, and `HashNode` does not override `__eq__`). But
this is the situation where they *should* compare equal--`HashNode.__new__`
should return the node in the table corresponding to that key.

Now suppose the new key is compared to a key in the table whose `value` and
`next_node` are not both alive. This should not actually be able to happen,
because the node such a key looks up holds strong references to the same
`value` and `next_node`, so they can't be dead unless that node is also dead.
But then the entry that maps that key to the node would have been removed. The
`WeakValueTable` is responsible for ensuring this happens before any new keys
are looked up in the table, even in a multithreaded scenario.

Still, even if that somehow did happen, there would be no false positive,
because the new key cannot compare equal to that key. Its `value` weakref would
have to be equal to the preexisting key's `value` weakref and its `next_node`
weakref would have to be equal to the preexisting key's `next_node` weakref.
But this is the scenario where at least one of the preexisting key's `value` or
`next_node` is dead. A dead weak reference never compares equal to a live weak
reference.

### Issue 2: False negatives

*When an attempt to construct a node should return an existing node instead of
making a new one, will the existing node actually be found in the table?*

We again have a new key, but this time there is a preexisting key it *should*
match. One way it could fail to match the preexisting key is if it wrongly
matches some other key in the table instead. But we saw in "Issue 1" that this
cannot happen. So all that remains to show is that it cannot fail to match the
correct key.

There are two ways keys could, in principle, not match. They could have
different hash codes, and therefore not even be compared. Or they could have
the same hash code but compare unequal.

A preexisting key that should be matched is one that maps an equal `value` and
identical `next_node` to a live preexisting node. The node it looks up is
alive, so the `value` and `next_node` it holds strong references to are, too.
So the new key has a weak reference to a live `value`, which is equal to the
`value` the preexisting key holds a weak reference to. Likewise, the new key
has a weak reference to a live `next_node`, which is equal to the `next_node`
the preexisting key holds a weak reference to.

Therefore, due to the behavior discussed above in "Weak reference equality
comparison semantics," the new and preexisting keys' `value` weakrefs are equal
and have equal hash code, and their `next_node` weakrefs are equal and have
equal hash codes. Since the keys are tuples of those (and tuples use structural
equality comparison and hash accordingly), the keys themselves are equal and
have equal hash codes.

### Issue 3: Can weakrefs' `__eq__`/`__hash__` make automatic deletion fail?

Entries that look up dead nodes are removed automatically from the table. The
`WeakValueTable` logic takes care of this automatically, and ensures the
underlying state of the table is not corrupted, even if multiple threads are
involved. But *how* are they removed?

#### Does the table look up keys with `==` and `hash` to remove them?

If you manually remove a key from a `WeakValueTable` with `del`, then of course
this will happen. But that is not the case at issue here.

When a weak reference callback for the node a key looks up is called, it seems
intuitive that this would not require its key to be looked up. After all, we
are already at the entry, and more importantly, the looked up node is a *value*
in the table, which does not facilitate looking up its key--so the table has to
have already access to the whole entry in order to remove the entry
efficiently. If this intuition is correct, then there is nothing more to worry
about. We don't have to reason out how comparisons to keys with dead weak
references work, if those comparison are never made, even to remove the keys.

Unfortunately, this intuition is *not* correct. `WeakValueTable` does not
promise not to search for the key of the entry it is removing. Furthermore, its
implementation in CPython stores entries in an underlying `dict`, to satisfy
its atomicity guarantees. Accordingly, it *always* subscripts that `dict` with
the key to remove it! Subscripting the `dict` calls `hash` on the key, and also
compares it for equality to one or more keys in the `dict`.

Therefore, we must reason about the hashing and equality comparison behavior of
our keys when one or both of their `value` and `next_node` weakrefs are dead.

#### Do our keys hash the same as themselves?

There are two bad hashing behaviors we need to make sure do not happen: failing
and raising `TypeError`, and returning different hash codes on different calls
to `hash`.

A key is a tuple of weak references to `value` and `next_node`, so its hash
code is based on the hash codes of those weak references. We're talking about a
key that is being deleted from the table, so that very same key object was
previously inserted into the table. When it was, the `WeakValueTable` called
`hash` on it, which called `hash` on the two weak references. Calling `hash` on
a weak reference to a non-hashable `value` raises `TypeError`, but we know the
`value` was hashable, and that both it and `next_node` were successfully
hashed, or the attempt to insert the would have failed.

As detailed in "Weak reference equality comparison semantics" above, a
`ref.weakref` object that has ever had `hash` called on it remembers its hash
code and returns it on all future `hash` calls, even if its referent has been
collected. So when the `WeakValueTable`'s underlying `dict` calls `hash` on the
key, the result is the same as before.

#### Do our keys compare equal to themselves?

As stated above in "Weak reference equality comparison semantics," weak
references that refer to the same object are always equal, even after the
object has been collected. A weak reference certainly refers to the same object
it refers to. So it is equal to itself. Thus a key's `value` weakref is equal
to itself, and its `next_node` weakref is equal to itself. So the key is equal
to itself.

#### Do our keys compare *un*equal to all other keys?

***FIXME: These are notes; I need to (re)write the material of this subsection.***

Suppose `r1` and `r2` are `weakref.ref` objects with immutable referents (that
is, the objects they refer to do not change in value) and `wr1 != wr2`. Then

When a key is removed, the weak references it holds may or may not still be
alive. (This is because, when a node becomes unreachable, its element and next
node may or may not still be reachable from other objects.)

If the weak references held by the key being removed are both still alive, then
they compare unequal to dead weak references, and because the table is never
allowed to have duplicate keys, they must compare unequal to any other keys in
the table whose weak references are both live. (See "Issue 1: False positives"
above for details.)

If the weak references held by the key being removed are both dead, then they
compare equal only to weak references to the same dead objects. In that case,
before the objects died, there had to have been duplicate keys. So this
possibility is excluded for the same reason.

If the key's `value` is dead and its `next_node` is alive,

[FIXME: rework] If one of the weak references held by the key being removed is
alive and the other is dead,


### Issue 4: Objects that can't be weakly referenced

***FIXME: The material below might require heavy editing.***

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
