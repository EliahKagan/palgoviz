"""Notes/scratchwork for decorators. See decorators.py."""


def does_nothing(func):
    # my_wrapper has the same behavior as func when called with 1 argument.
    # But they are not the same function.
    def my_wrapper(arg):
        return func(arg)
    return my_wrapper


def does_nothing_2(func):
    # This returns func itself.
    return func
