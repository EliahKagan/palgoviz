#!/usr/bin/env python

"""
The classic "FizzBuzz" problem, implemented using match-case.

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
        match (x % 5, x % 3):
            case (0, 0): 
                print('FizzBuzz')
            case (0, _): 
                print('Buzz')
            case (_, 0):
                print ('Fizz')
            case (_, _):
                print(x)


if __name__ == '__main__':  # If we are running this module as a script.
    fizzbuzz()