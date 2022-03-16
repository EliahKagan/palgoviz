"""How variable scoping works in Python."""

x = 'outer'


# Even though python is dynamically typed, it is statically scoped.
# This is why the result of this is an exception,
# f() attempts to print the "local variable x," which doesn't exist
def f():
    print(x)
    x = 'inner'


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
        square = 50  # Makes no difference.
        print(f'Calling {printer.__name__}:', end='  ')
        printer()


def call_h():
    print(x)
    h()
    print(x)
