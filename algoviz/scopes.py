"""How variable scoping works in Python."""

x = 'outer'


# Even though python is dynamically typed, it is statically scoped. That's why
# "print(x)" in this function raises an UnboundLocalError exception. f()
# attempts to print the *local variable* x, which doesn't exist.
def f():
    # flake8 says: F823 local variable 'x' defined in enclosing scope on line 3
    #              referenced before assignment
    #
    print(x)  # noqa: F823

    # flake8 says: F841 local variable 'x' is assigned to but never used
    x = 'inner'  # noqa: F841


def g():
    x = "outer"
    print(x)

    def inner():
        nonlocal x
        x = "OUTER"

    inner()
    print(x)


def h():
    global x
    x = "global"


def demo():
    f()
    print(x)


def make_square_printer(x):
    def printer():
        print(square)

    square = x**2

    return printer


def test_printers():
    printers = []
    for n in 2, 3, 7:
        printers.append(make_square_printer(n))

    # print(printers)

    for printer in printers:
        # Assigning to the local variable square makes no difference to the
        # variable in the global scope (nor the enclosing scope). flake8 says:
        #
        # F841 local variable 'square' is assigned to but never used
        #
        square = 50  # noqa: F841

        print(f'Calling {printer.__name__}:', end='  ')
        printer()


def call_h():
    print(x)
    h()
    print(x)
