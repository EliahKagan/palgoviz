#!/usr/bin/env python

# Copyright (c) 2022 David Vassallo and Eliah Kagan
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
The classic "FizzBuzz" problem.

    Write a program that prints the integers 1 through 100 (inclusive), one per
    line, to standard output.

    Except:

      - For multiples of 3, print "Fizz", and don't print the number.
      - For multiples of 5, print "Buzz", and don't print the number.
      - For multiple of both 3 and 5, print both "Fizz" and "Buzz".

    Don't print the quotes. Also, when printing both "Fizz" and "Buzz" for a
    number, they go on the same line as each other, with no separation.

    For example, the tenth through fifteenth lines of the output should be:

        Buzz
        11
        Fizz
        13
        14
        FizzBuzz

    This docstring uses indentation, but no line of output should contain any
    leading or trailing whitespace.
"""


def fizzbuzz():
    for x in range(1, 101):
        if (x % 5 == 0) and (x % 3 == 0):
            print("FizzBuzz")
        elif x % 5 == 0:
            print("Buzz")
        elif x % 3 == 0:
            print("Fizz")
        else:
            print(x)


if __name__ == '__main__':  # If we are running this module as a script.
    fizzbuzz()
