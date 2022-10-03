# `sll.HashNode` subtleties

## Solution to the problem of heterogeneous cycles

In many uses, client code can ensure no heterogeneous cycle forms. But that's
not always feasible. Furthermore, the whole point of cyclic garbage collection
is that even arbitrary cycles do not cause leaks. So it would be good if the
node type could avoid keeping strong references to any heterogeneous cycles no
longer reachable except through its private table. Because a node's element and
successor always exist for as long as the node exists--since the node holds
strong references to them--it seems the references to them from the table could
be weak instead of strong.

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
