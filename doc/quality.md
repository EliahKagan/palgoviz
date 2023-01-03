# Code Quality Considerations

## Project status

***palgoviz is a work in progress.***

Most functions and classes in modules (`.py` files) inside the `palgoviz/`
package are intended to be suitable for use as exercises, if you remove their
implementations other than the header and docstring. For a few, the suggested
way to “reset” them as exercises is different, and documented.

On the *main* branch, nearly all functions and classes in modules in
`palgoviz/` have been reviewed, and fully tested as exercises, by each of us.
We usually do not merge module code to *main* until this has been done.

The major exception, as of this writing, is `sll.py`, which has not yet been
doubly vetted in this way. The “`alr`” exercises in `recursion.py` have also
not been through this process (but the others there have).

## Unit tests

Like the doctests, the unit tests in `tests/` are intended, in part, to support
reworking the code under test as exercises. However, they do not always test
all stated requirements. In many cases, this is intentional; for example, they
do not ensure asymptotic time complexity is as documented. As in software
engineering more generally, it’s a good sign when all tests pass, but it
doesn’t prove correctness.

Some of the unit tests in `tests/` could *themselves* be turned into exercises
through the removal of some material. `test_adders.py` and `test_simple.py`
have been tested out in this use, but most others have not. Some of them would
only be useful as more advanced exercises than the code under test (e.g.,
`test_context.py`,`test_functions.py`).

## Approach

This project is oriented toward a teaching approach that:

- presents doctests first, then `unittest` tests.
- defers the use of type annotations until after Python’s dynamic type system
  is well understood and practiced.
- defers data classes until after more manual techniques, and the Python data
  model, have been covered in detail.

This is not objectively better than other approaches. Materials here can be
used when taking other approaches, though sometimes they may require greater
adaptation.

A disadvantage of the doctests-first approach is that we have a lot of really
long doctests, especially in `gencomp1.py` and `gencomp2.py`. In some cases,
that may be considered a bug. Furthermore, a disadvantage of teaching
`unittest` before (or instead of) `pytest` is that `pytest` is widely used and
loved by Python programmers, for good reason, and may be the more valuable
framework to learn.
