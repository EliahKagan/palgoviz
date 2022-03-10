#!/usr/bin/env python

"""Hola saluda al user en español. (Hola greets the user in Spanish.)"""

from greet import make_greeter


def run():
    """Run as a script."""
    name = input("¿Como se llama usted? ")
    greeter = make_greeter('es')
    greeter(name.strip())  # strip() drops leading and trailing whitespace.


if __name__ == '__main__':  # If we are running this module as a script.
    run()
