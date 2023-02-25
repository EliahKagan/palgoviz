#!/usr/bin/env python

# Copyright (c) 2021, 2022 David Vassallo and Eliah Kagan
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

"""
Very basic demonstration of the match...case statement.

For more interesting uses, along the lines of what match...case was actually
introduced to the language to facilitate, see assign2.ipynb.
"""

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
        print('You should pass an integer.')
    except IndexError:
        print('You should pass something, an integer in particular.')
    else:
        echo_num(number)
    finally:
        print('Bored now.')


if __name__ == '__main__':
    run()
