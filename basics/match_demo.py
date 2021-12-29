#!/usr/bin/env python

import sys

"""Demonstration of the match...case command."""


def echo_num(number):
    """Show the match command."""
    match number:
        case 1:
            print('You said one.')
        case 2:
            print('You said two.')
        case 3:
            print('You said three.')
        case _:  # Discards must go below anything more specific.
            print('You said something else.')


def run():
    """Run as a script."""
    number = int(sys.argv[1])
    echo_num(number)


if __name__ == '__main__':
    run()
