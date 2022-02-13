#!/usr/bin/env python

"""FizzBuzz (as in fizzbuzz.py), but with 6 and 9 instead of 3 and 5."""


def fizzbuzz():
    for x in range(1, 101):
        if x % 18 == 0:
            print("FizzBuzz")
        elif x % 9 == 0:
            print("Buzz")
        elif x % 6 == 0:
            print("Fizz")
        else:
            print(x)


if __name__ == '__main__':  # If we are running this module as a script.
    fizzbuzz()
