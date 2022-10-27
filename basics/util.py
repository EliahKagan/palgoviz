"""
Broadly useful utility functions used by multiple modules.

This module is a bikeshed, like testing.py, but for functions that are not
specific to testing, yet still neither belong in any other module nor currently
justify the creation of more specific modules to contain them.
"""


def identity_function(arg):
    """
    Return the argument unchanged.

    Compared to lambda x: x, this has a meaningful name and is less confusing
    inside complicated expressions. But that's not what justifies having this.

    Rather, rebinding an existing variable to lambda x: x looks wrong, because
    it is usually a mistake to write an assignment statement whose right-hand
    side is just a lambda expression, because that's what the def statement is
    for. But using a def statement to *re*bind a name looks wrong, because it
    is usually either an accidental redefinition or an accidental name clash.
    So both ways to replace a sentinel with an identity function are imperfect.

    Many tools and Python-using humans rightly think this looks like a bug:

        if f is None:
            f = lambda x: x

    Many tools and Python-using humans rightly think this looks like a bug too:

        if f is None:
            def f(x):
                return x

    Robot and human alike are usually okay with this:

        if f is None:
            f = identity_function
    """
    return arg
