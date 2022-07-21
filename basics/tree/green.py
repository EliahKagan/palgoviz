"""
Binary tree DFS generator functions delegating to tree.dfs, using greenlets.

tree.dfs is a recursive DFS implementation that traverses a binary tree and
does any combination of preorder, inorder, and postorder actions by calling
f_pre, f_in, or f_post functions passed as optional keyword-only arguments.

Since tree.dfs claims to be a generalization of tree.preorder, tree.inorder,
and tree.postorder, it should be possible to make alternative implementations
of them that delegate traversal to tree.dfs. This submodule contains those
implementations. [!!FIXME: Move the docstring text below to green.md or .rst.]

To identify the challenge to be overcome, first consider a situation with three
functions: a generator function g that yields values, a function f that we want
called with each value, and a function h that makes that happen. h calls g and
iterates over the returned generator object, calling f in each iteration:

```python
    def h():
        for x in g():
            f(x)
```

Note that this works lazily: f is called for each value yielded from g before
control reenters g to compute the next value. Yet the code is simple. This is
because g is a generator function, and generators are a mechanism to do just
this sort of thing: to allow code to lazily consume a stream of values that
another function produces by resuming (or starting), yielding, and suspending.

Now consider the opposite situation: g is a regular function, not a generator
function, and it doesn't return its results. Instead, it accepts a function f
as an argument. For each result g produces, it calls f with the result. All
calls to f happen in a single call to g. How do we write a generator function h
that yields each value g passes to f? h can pass whatever f it likes to g, but
the code of g cannot be modified.

If we wanted to do it eagerly, it is straightforward:

```python
    def h():
        a = []
        g(a.append)
        yield from a  # Why is h even a generator function?
```

But we really want to do it lazily. Each time g calls f, h should yield the
value f received, before g calls f again (or before g returns, if that was the
last time g was going to call f). Being quite general, g doesn't know we want
this kind of concurrency. So whatever mechanism we use to make g suspend when
it calls f, and to make g resume after h yields the value f was called with,
will itself be external to g.

One approach might be to avoid solving the problem altogether, and report a bug
in g, claiming g should just be a generator function in the first place. That
would often be right. But sometimes there may be a reason g was not written as
a generator function. One possible reason is if g is a function in a native
code library that doesn't know anything about Python, being called from Python.

Here, another reason applies. g is tree.dfs, and f is any of f_pre, f_in, or
f_post. tree.dfs calls separate functions for preorder, inorder, and postorder
actions because you may want to use more than one. It could have been a
generator function that yielded objects that both carry values and specify if
they are preorder, inorder, or postorder results, letting the consumer filter
them. But it is not obvious that this would be better, since many simple uses
would become more complicated. (Another situation is if g were a function in a
native code library that doesn't know anything about Python.)

FIXME: Finish this docstring. But maybe move most of it to an .md or .rst file.
"""

from greenlet import greenlet as _greenlet

import tree as _tree


def _adapt(produce):
    """Convert a function passing results to a function into a generator."""
    main = _greenlet.getcurrent()

    def receive(value):
        main.switch(value)

    sub = _greenlet(lambda: produce(receive))

    while True:
        result = sub.switch()
        if sub.dead:
            break
        yield result


def preorder_via_general_dfs(root):
    """Preorder traversal, delegating to tree.dfs but yielding elements."""
    return _adapt(lambda receive: _tree.dfs(root, pre_fn=receive))


def inorder_via_general_dfs(root):
    """Inorder traversal, delegating to tree.dfs but yielding elements."""
    return _adapt(lambda receive: _tree.dfs(root, in_fn=receive))


def postorder_via_general_dfs(root):
    """Postorder traversal, delegating to tree.dfs but yielding elements."""
    return _adapt(lambda receive: _tree.dfs(root, post_fn=receive))


__all__ = [thing.__name__ for thing in (
    preorder_via_general_dfs,
    inorder_via_general_dfs,
    postorder_via_general_dfs,
)]
