"""
How variable scoping works in Python.
"""

x = 'outer'


# Even though python is dynamically typed, it is statically scoped. 
# This is why the result of this is an exception, 
# f() attempts to print the "local variable x," which doesn't exist 
def f():
    print(x)
    x = 'inner'


def demo():
    f()
    print(x)


def make_square_printer(x):
    square = x**2

    def printer():
        print(square)
    
    return printer


printers = []
for n in 2, 3, 7:
    printers.append(make_square_printer(n))

# print(printers)

for printer in printers:
    square = 50  # Makes no difference.
    print(f'Calling {printer}:', end='  ')
    printer()

