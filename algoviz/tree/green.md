# Theory behind `tree.green`

`tree.general_dfs` is a recursive
[DFS](https://en.wikipedia.org/wiki/Depth-first_search) implementation that
traverses a [binary tree](https://en.wikipedia.org/wiki/Binary_tree) and does
any combination of [preorder, inorder, and
postorder](https://en.wikipedia.org/wiki/Tree_traversal) actions by calling
`f_pre`, `f_in`, or `f_post` functions passed as optional keyword-only
arguments.

Since `tree.general_dfs` claims to be a generalization of `tree.preorder`,
`tree.inorder`, and `tree.postorder`, it must be possible to make alternative
implementations of them that delegate traversal to `tree.general_dfs`. The
`tree.green` submodule contains those implementations.

To identify the challenge to be overcome, first consider a situation with three
functions: a generator function `produce` that yields values, a function
`receive` that we want called with each value, and a function `adapt` that
makes that happen. `adapt` calls `produce` and iterates over the returned
generator object, calling `receive` in each iteration:

```python
def adapt(produce, receive):
    for result in produce():
        receive(result)
```

Note that this works lazily: `receive` is called for each value yielded from
`produce` before control reenters `produce` to compute the next value. Yet the
code is simple. This is because `produce` is a generator function, and
generators are a mechanism to do just this sort of thing: to allow code to
lazily consume a stream of values that another function produces by resuming
(or starting), yielding, and suspending.

Now consider the opposite situation: `produce` is a regular function, not a
generator function, and it doesn't return its results. Instead, it accepts a
function `receive` as an argument. For each result `produce` produces, it calls
`receive` with the result. All calls to `receive` happen in a single call to
`produce`. How do we write a generator function `adapt` that yields each value
that `produce` passes to `receive`? `adapt` can pass whatever `receive` it
likes to `produce`, but the code of `produce` cannot be modified.

If we wanted to do it eagerly, it is straightforward:

```python
def adapt(produce):
    results = []
    produce(receive=results.append)
    yield from results  # Why is adapt even a generator function?
```

But we really want to do it lazily. Each time `produce` calls `receive`,
`adapt` should yield the value `receive` received, before `produce` calls
`receive` again (or before `produce` returns, if that was the last time
`produce` was going to call `receive`).

Being quite general, `produce` doesn't know we want this kind of concurrency.
So whatever mechanism we use to make `produce` suspend when it calls `receive`,
and to make `produce` resume whenever `adapt` resumes after yielding the value
`receive` was called with, will itself be external to `produce`.

One approach might be to avoid solving the problem altogether, and report a bug
in `produce`, claiming `produce` should just be a generator function in the
first place. That would often be right. But sometimes there may be a reason
`produce` was not written as a generator function. One possible reason is if
`produce` is a function in a native code library that doesn't know anything
about Python, being called from Python.

Here, another reason applies. `produce` is `tree.general_dfs`, and `receive` is
any of `f_pre`, `f_in`, or `f_post`. `tree.general_dfs` calls separate
functions for preorder, inorder, and postorder actions because you may want to
use more than one. It could have been a generator function that yielded objects
that both carry values and specify if they are preorder, inorder, or postorder
results, letting the consumer filter them. But it is not obvious that this
would be better, since many simple uses would become more complicated.

So how do we pass `produce` a function that, when called, *suspends* execution
and switches back to code in `adapt` that can then yield a result?

This kind of concurrency used to be commonplace: old operating systems, like
Windows 3.1, used
[cooperative](https://en.wikipedia.org/wiki/Cooperative_multitasking) rather
than
[preemptive](https://en.wikipedia.org/wiki/Preemption_(computing)#PREEMPTIVE)
multitasking. It can be used today *within* an application, though it often
requires library support. Consider the following model:

- A [*process*](https://en.wikipedia.org/wiki/Process_(computing)) represents a
  running executable, and has a virtual address space, which enforces memory
  boundaries. Code of a process runs in one or more threads.

- A [*thread*](https://en.wikipedia.org/wiki/Thread_(computing)) is a sequence
  of instructions, maintained by its own instruction pointer and call stack.
  Threads are preemptively multitasked. Threads, from all processes running on
  the system, are given time slices (of perhaps 1/60 of a second) on CPU cores,
  provisioned by the operating system's thread scheduler. That is, the kernel
  ensures that processing switches rapidly between all threads on the system
  that have work to do. Code running in a thread need not, and usually does
  not, explicitly yield control to other threads.

- A [*fiber*](https://en.wikipedia.org/wiki/Fiber_(computer_science)) is also a
  sequence of instructions, maintained by its own instruction pointer and call
  stack. *Fibers are cooperatively multitasked.* Whenever a thread is
  executing, it is executing the code of exactly one fiber. A fiber runs until
  it finishes or explicitly yields control. Until the running fiber yields
  control, all other fibers belonging to the same thread are blocked.

Some threading models don't incorporate fibers. But because they are
cooperative, their functionality can often be supplied by a library. (Some
authors regard fibers to be cooperatively multitasked sequences of instructions
*managed by the operating system*, but I do not use that convention here.)

Does Python have fibers? Arguably, yes, in limited ways. Generator objects have
their own call stacks, and their own instruction pointers in the sense of
states keeping track of where in the generator's code execution will resume.
Asynchronous functions likewise have their own call stacks, and their own
instruction pointers in the sense of states keeping track of where they will
resume after awaiting another coroutine or other awaitable.

Generator functions and asynchronous functions rely on Python language
features, supported by syntax. A generator function contains `yield` or `yield
from`, returns a generator object before any of its code is run, and results
are accessed by iteration or manually calling `next`. An asynchronous function
is defined with `async def` and returns a coroutine object before any of its
code is run, and results are accessed by using the `await` operator to await
that object or an object derived from it (such as by `asyncio.create_task`), or
by passing it to `asyncio.run` to run it as the entry point of a new event
loop.

`tree.general_dfs` calls `f_pre`, `f_in`, and `f_post` synchronously and is not
a generator function or asynchronous function. So lazily delegating to it from
a generator is a case that calls for a use of fibers separate from what can be
achieved with Python syntax.

**The [`greenlet`](https://greenlet.readthedocs.io/en/latest/) library**
supplies this ability. Greenlets are fibers (in the sense defined above). Any
greenlet can switch to any other greenlet (in the same thread) by calling its
`switch` method, and may pass arguments to that method. A greenlet resumes from
its call to `switch` when some other greenlet switches back to it.

Here's a lazy version of the above `adapt` function, using greenlets:

```python
from greenlet import greenlet
```

```python
def adapt(produce):
    main = greenlet.getcurrent()
    sub = greenlet(lambda: produce(receive=main.switch))

    while True:
        result = sub.switch()
        if sub.dead:
            break
        yield result
```
