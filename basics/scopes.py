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
