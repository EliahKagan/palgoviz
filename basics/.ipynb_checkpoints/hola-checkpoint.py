#!/usr/bin/env python

"""Hola saluda al user en español. (Hola greets the user in Spanish.)"""

from greet import hello


def run():
    """Run as a script."""
    name = input("¿Como se llama usted? ")
    hello(name.strip(), 'es')  # strip() drops leading and trailing whitespace.


if __name__ == '__main__':  # If we are running this module as a script.
    run()
