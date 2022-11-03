"""Notes/scratchwork for decorators. See decorators.py."""


def does_nothing(func):
    # mywrapper has the same behavior as func when called with 1 argument.
    # But they are not the same function.
    def mywrapper(arg):
        return func(arg)
    return mywrapper


def does_nothing_2(func):
    # This returns func itself.
    return func
