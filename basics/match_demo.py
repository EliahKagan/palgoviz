#!/usr/bin/env python

"""Demonstration of the match...case command."""

import sys


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
    try:
        number = int(sys.argv[1])
    except ValueError:
        print(f'You should pass an integer')    
    except IndexError: 
        print('You should pass something, an integer in particular')
    else:
        echo_num(number)
    finally: 
        print('Bored now')


if __name__ == '__main__':
    run()
