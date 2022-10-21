# `sll.HashNode` subtleties

***WARNING*: This file contains SPOILERS, if you are implementing anything in
`sll.py` as an exercise!**

## Solution to the problem of heterogeneous cycles

*See `test_sll.TestHashNodeHeterogeneousCycles` for how we are defining this
problem.*

In many uses, client code can ensure no heterogeneous cycle forms. But that's
not always feasible. Furthermore, the whole point of cyclic garbage collection
is that even arbitrary cycles do not cause leaks. So it would be good if the
node type could avoid keeping strong references to any heterogeneous cycles no
longer reachable except through its private table.

In a design that does not aim to avoid the problem of heterogeneous cycles,
nodes hold strong references to their elements and successors. So a node's
element and successor live at least as long as the node.

```python
cls._table[value, next_node] = node
```

The table entry for a node goes away when the node is collected, so it seems
the table's references to the element and successor could be weak instead of
strong. Maybe this would work:

```python
cls._table[weakref.ref(value), weakref.ref(next_node)] = node
```

The key there is a tuple of two weak references. Tuples use structural equality
comparison. So the weak references to `value` and `next_node` participate in
calls to `__eq__` and `__hash__` on the key, when it is looked up in the table.

We must attend to several issues, to determine if *any* approach like this
could possibly be correct and, if so, whether the simple approach of using a
tuple of the weak references is actually sufficient:

1. **False positives.** When an attempt to construct a node should create a new
   node, will a false positive match to an existing entry in the table always
   be avoided?

2. **False negatives.** When an attempt to construct a node should return an
   existing node instead of creating a new one, will the existing node actually
   be found in the table?

3. **Can weakrefs' `__eq__`/`__hash__` break removal?** When a node becomes
   unreachable and is removed from the table, what happens? Do we need to worry
   about the removal operation, behind the scenes, looking up the key by
   calling `__hash__` and `__eq__` on weak references to dead objects?

4. **Objects that can't be weakly referenced.** Is it a problem that not all
   objects in Python are weak-referenceable?

5. **NaN-like objects.** Are pathological elements, like floating-point NaNs,
   that are not equal even to themselves—yet are hashable!—still handled
   properly?

All these issues, except *#4*, relate to how `weakref.ref` objects behave under
equality comparison. *Issue #5* is deliberately ignored until the end, because
*(a)* insights from considering the previous issues have bearing on it, and
*(b)* if necessary, we could stop permitting such objects, raising `ValueError`
from `HashCode.__new__` if one is passed as an element.

Before examining any of those five issues, though...

### Why not just use `weakref.proxy` instead of `weakref.ref`?

The table key for a node holds weak references to its element and successor.
When they are still live, it seems we want them to contribute to the key's
hashing and equality comparison behavior the same as if they were actually
elements of the key—that is, as if the key were just a tuple of (strong
references to) them. This raises the question of whether we should use weakref
*proxies* instead.

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

`weakref.ref` objects are equal if the objects they refer to are *(a)* both
live and equal to each other or *(b)* the same object and dead. Otherwise they
are not equal.

> Weak references support tests for equality, but not ordering. If the
> referents are still alive, two references have the same equality relationship
> as their referents (regardless of the *callback*). If either referent has
> been deleted, the references are equal only if the reference objects are the
> same object.

We defer consideration of objects that are not equal to themselves until *Issue
#5: NaN-like objects* below. Under this assumption of no non-self-equal
referents, `weakref.ref` objects are equal when *(α)* they reference the same
object, even if that object has been collected, or *(β)* they reference
different objects, both of which are still live, that are equal to each other.
Weak references to immutable objects may thus go from being equal to unequal,
but never from being unequal to equal.

#### Hashing

`weakref.ref` objects hash based on their referents (the objects they refer
to).

> Weak references are
> [hashable](https://docs.python.org/3/glossary.html#term-hashable) if the
> *object* is hashable. They will maintain their hash value even after the
> *object* was deleted. If
> [`hash()`](https://docs.python.org/3/library/functions.html#hash) is called
> the first time only after the *object* was deleted, the call will raise
> [`TypeError`](https://docs.python.org/3/library/exceptions.html#TypeError).

Calling `hash` on a `weakref.ref` for the first time raises `TypeError` if its
referent is already dead. Otherwise, its hash code is based on the referent's
hash code (so it is consistent with equality comparison), and the weak
reference also caches the hash code, never calling `hash` on the referent more
than once. Even after the referent dies, calling `hash` on the weak reference
returns the same hash code.

### Issue #1: False positives

*When an attempt to construct a node should create a new node, will a false
positive match to an existing entry in the table always be avoided?*

To subscript the table, a key is constructed, holding weak references to
`value` and `next_node`. These are weak references to live objects—their
referents, at this point, are local variables of the executing function. (More
precisely, they are the local variables' strong referents.) This new key may,
in the worst case, have to be compared to every key already in the table. Can
it compare equal to a key it shouldn't?

Suppose the new key is compared to a key in the table whose `value` and
`next_node` are both live. Since all weak references being compared refer to
live objects, the effect is the same as comparing the objects themselves. Thus,
if the new key compares equal to the preexisting key, then the new key's
`value` is equal to the preexisting `value`, and the new key's `next_node` is
the same object as the preexisting `next_node` (since we ensure `next_node` is
always a `HashNode` object, and `HashNode` does not override `__eq__`). But
this is the situation where they *should* compare equal—`HashNode.__new__`
should return the node in the table corresponding to that key.

Now suppose the new key is compared to a key in the table whose `value` and
`next_node` are not both live. This should not actually be able to happen,
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
`next_node` is dead. A `weakref.ref` to a dead object never compares equal to a
`weakref.ref` to a live object.

### Issue #2: False negatives

*When an attempt to construct a node should return an existing node instead of
making a new one, will the existing node actually be found in the table?*

We again have a new key, but this time there is a preexisting key it *should*
match. One way it could fail to match the correct key in the table is if it
wrongly compares equal to some other key in the table first. But we saw in
*Issue #1: False positives* that this cannot happen. So all that remains to
show is that *(a)* it and the correct key will hash the same, so they will
eventually be compared, and *(b)* when they are actually compared, they will
come out equal.

A preexisting key that should be matched is one that maps an equal `value` and
identical `next_node` to a live preexisting node. The node it looks up is live,
so the `value` and `next_node` it holds strong references to are, too. So the
new key has a weak reference to a live `value`, which is equal to the `value`
the preexisting key holds a weak reference to. Likewise, the new key has a weak
reference to a live `next_node`, which is equal to the `next_node` the
preexisting key holds a weak reference to.

Therefore, due to the behavior discussed above in *Weak reference equality
comparison semantics*, the new and preexisting keys' `value` weakrefs are equal
and have equal hash code, and their `next_node` weakrefs are equal and have
equal hash codes. Since the keys are tuples of those (and tuples use structural
equality comparison and hash accordingly), the keys themselves are equal and
have equal hash codes.

### Issue #3: Can weakrefs' `__eq__`/`__hash__` break removal?

*When a node becomes unreachable and is removed from the table, what happens?
Do we need to worry about the removal operation, behind the scenes, looking up
the key by calling `__hash__` and `__eq__` on weak references to dead objects?*

Entries that look up dead nodes are removed from the table. The
`WeakValueTable` logic takes care of this automatically, and ensures the
underlying state of the table is not corrupted, even if multiple threads are
involved. But *how* are they removed?

#### Does the table look up keys with `==` and `hash` to remove them?

If you manually remove a key from a `WeakValueTable` with `del`, then of course
this will happen. But that is not the case at issue here.

When the weak reference callback the table has registered for a node is called,
it seems intuitive to think this callback does not need to subscript the table.
The callback must already contain information on the entry, and why would the
table need to look something up in itself? If this intuition were correct,
there would be nothing more to worry about. We wouldn't have to reason out how
comparisons to keys with weak references to dead objects work, if those
comparisons are never made, even to remove the keys.

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
code is based on the hash codes of those weak references. The key being deleted
was found in the table—it is not merely equal to a key that was inserted, but
the same object. When it was inserted, the table called `hash` on it, which
called `hash` on the two weak references. Calling `hash` on a weak reference to
a non-hashable `value` raises `TypeError`, but we know the `value` was
hashable, and that both it and `next_node` were successfully hashed, or the
attempt to insert the key would have failed.

As detailed in *Weak reference equality comparison semantics* above, a
`ref.weakref` object that has ever had `hash` called on it remembers its hash
code and returns it on all future `hash` calls, even after its referent is
dead. So when the `WeakValueTable`'s underlying `dict` calls `hash` on the key,
the result is the same as before.

#### Do our keys compare equal to themselves?

As stated above in *Weak reference equality comparison semantics*, because we
are assuming self-equality, weak references that refer to the same object are
always equal, both before and after the object dies. A weak reference certainly
refers to the same object it refers to. So it is equal to itself. Thus a key's
`value` weakref is equal to itself, and its `next_node` weakref is equal to
itself. So the key is equal to itself.

#### Do our keys compare *un*equal to all other keys?

When a key is removed:

- The weak references it holds may or may not have live referents. This is
  because, when a node becomes unreachable, its element and successor may or
  may not still be separately reachable from other objects.

- Surprisingly, the weak references held by the *other* keys it is compared to
  may or may not have live referents. The usual reason they must—that a node
  keeps its `value` and `next_node` alive, so if they are dead, then the node
  is dead and its entry in the table has been automatically removed—does not
  apply here. The `WeakValueTable` guarantees no entry that would look up a
  dead object is ever observed, from the outside, to be in the table. But
  multiple nodes can effectively die at the same time. They have to be removed
  in some order.

  (There another situation when a `WeakValueTable`'s underlying `dict` may
  temporarily hold multiple stale entries. To remove an entry from a `dict`
  while iterating through the `dict` is a bug and behaves unpredictably. But if
  the `WeakValueTable` is not being explicitly mutated, then iterating through
  *it* is permitted. In such a situation, it avoids yielding stale entries, but
  it waits to remove them from its `dict` until iteration either finishes or
  becomes invalid by explicit mutation of the table.)

Entries are automatically removed from the table, but they are never
automatically added. Adding an entry is explicit, and any stale entries in the
table's underlying `dict` are removed before it is performed. So when a key is
automatically removed, and it is looked up in order to make that happen, it is
only compared against keys that have *existed in the table at the same time it
did*. This is fantastic news, because duplicate keys are not allowed in the
table.

It is therefore sufficient to show that keys that were once unequal never
become equal.

Suppose keys `(vr1, nnr1)` and `(vr2, nnr2)` are unequal. Then `vr1 != vr2` or
`nnr1 != nnr2`. For the keys to become equal in the future would require that,
in the future, both `vr1 == vr1` and `nnr1 == nnr2`. Therefore, either the weak
references `vr1` and `vr2` to the elements must start out unequal and become
equal, or the weak references `nnr1` and `nnr2` to the successors must start
out unequal and become equal.

The elements and the successors are immutable. As stated above in *Weak
reference equality comparison semantics*, because we are assuming no referent
is unequal to itself, `weakref.ref` objects that compare unequal and whose
referents are immutable will never compare equal. Therefore, element weakrefs
can't go from unequal to equal, nor can successor weakrefs, so keys can't
either. A key being removed therefore compares unequal to any other key.

### Issue #4: Objects that can't be weakly referenced

*Is it a problem that not all objects in Python are weak-referenceable?*

Not all objects in Python can be referred to by weak references. This is a
serious problem for us.

In this code, reproduced from above, `weakref.ref(value)` only succeeds if
elements are weak-referenceable, and `weakref.ref(next_node)` only succeeds if
successors are weak-referenceable:

```python
cls._table[weakref.ref(value), weakref.ref(next_node)] = node
```

#### The one successor that cannot be weak-referenced

`next_node` is always a `HashNode` instance or the `None` object.

Every `HashNode` instance is weak-referenceable. We made `HashNode` and ensured
this. If we hadn't, we could not have used them as values in a
`WeakValueDictionary` in the first place.

The `None` object, however, is not weak-referenceable. We can solve this by
using our own singleton instead. But that may be overkill, since we can just
use `None` *directly*:

```python
weak_next_node = None if next_node is None else weakref.ref(next_node)
cls._table[weakref.ref(value), weak_next_node] = node
```

That can be written more simply, because before doing this, we have already
verified that `next_node` is either `None` or a `HashNode` instance. The only
way `next_node` is falsy is if it is `None`. So:

```python
cls._table[weakref.ref(value), next_node and weakref.ref(next_node)] = node
```

#### Elements that cannot be weak-referenced

It would be bad to support only weak-referenceable elements—for example, we
couldn't even store `int` values.

The insight to solve this is that a chain is only as strong as its weakest
link. We don't actually need to refer directly any element by a weak reference.
We can instead refer to a *wrapper* object by a weak reference, where the
wrapper refers to the element by a strong reference.

Suppose our custom wrapper type is called `_Box`. Then we will have:

```python
box = _Box(value)
cls._table[weakref.ref(box), next_node and weakref.ref(next_node)] = node
```

To make that work, `_Box` must delegate equality comparison and hashing to the
wrapped `value`.

The `_Box` instance itself must be kept alive somehow. Currently it is only
referred to by a weak reference in a key, and by a strong reference in a local
variable that goes away when `HashNode.__new__` returns.

`value` and `next_node` stay alive as long as the node, which itself holds
strong references to them. We likewise can keep the box alive by having the
node hold a strong reference to it in a non-public attribute. This *could* be
separate from the node's `value` and `next_node`. But the redundancy can be
avoided by having the node contain its `value` only indirectly through the box.

(Note that this kind of "box" is only tangentially related to *boxing* in
languages like Java and C#, where some types are value types, some types are
reference types, and a value type instance can be boxed in a reference type
object to allow it to be accessed through a reference and stored on a managed
heap. In Python, all types are reference types, "box" has no formal meaning,
and our `_Box` class is merely a wrapper that conceptually "contains" the
object it stands in front of. Arguably `_Box` should be named something else.)

### Issue #5: NaN-like objects

*Are pathological elements, like floating-point NaNs, that are not equal even
to themselves—yet are hashable!—still handled properly?*

Recall the old approach, from before the heterogeneous cycle problem was
solved, where each node's key held strong references to the node's element and
successor:

```python
cls._table[value, next_node] = node
```

That worked with NaNs (and other objects not equal to themselves). Attempting
to construct a second node with the same `value` object and the same
`next_node` returned the original node, rather than creating a duplicate.

It worked automatically when `value` was an element of a `tuple`, because
sequence and hash-based containers in the Python standard library use both `==`
and `is` checks in their structural equality comparisons. `math.nan !=
math.nan`, but `(math.nan,) == (math.nan,)`, and likewise, `(value, next_node)
== (value, next_node)` even when `value != value`.

Standard library containers do this to accommodate NaNs. This behavior is
particularly important in `dict` and `set`, where otherwise the same NaN object
could be inserted many different times as a key, would be stored that many
times, and would never be found. The same considerations apply to
`HashNode`—but more so, because all code in the whole program that uses
`HashNode` shares a single, global table of nodes, behind the scenes.

Unlike structural equality comparison of standard library containers,
`weakref.ref` equality comparison with live referents does *not* include an
`is` check. So the changes described above that solve the heterogenous cycle
problem break handling of NaN and NaN-like objects.

Furthermore, the reasoning given in preceding sections about correctness
explicitly assumed no non-self-equal object will ever be used as an element.
That assumption is unreasonable. If necessary, we could check that `value ==
value` and raise `ValueError` in `HashNode.__new__` otherwise, prohibiting such
elements while safeguarding shared state. But it would be better to support
them.

This is another problem that can be solved by wrapping the element in a "box"
that has the desired behavior. That's not the only way to solve it. Another
approach is for keys to be instances of a custom class that provides the
desired equality comparison behavior, rather than tuples. That might be the
better approach, if we weren't *already* wrapping.

`_Box.__eq__` checks the type of `other`, like most `__eq__` implementations,
but when `other` is a `_Box`, it returns:

```python
self.value == other.value
```

To make it so `_Box` instances are also equal when their values are the same
object, regardless of whether that object is equal to itself, that can be
changed to:

```python
self.value is other.value or self.value == other.value
```

With that change, `_Box` solves both the problem of elements that are not
weakly referenceable and the problem of elements that compare unequal to
themselves.

<!--
    FIXME: Add a section about how solving the problem of heterogeneous cycles
    unfortunately makes it much more feasible than before to produce duplicate
    nodes by resurrecting a node after it is removed from the WeakValueTable.
-->
