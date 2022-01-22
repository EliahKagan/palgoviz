"""
How variable scoping works in Python.
"""


def f():
    if True:
        x = 'inner'
    print(x)


x = 'outer'

f()
print(x)
