<!-- SPDX-License-Identifier: 0BSD -->

# Readme on `fib5k` files

The `fib5k` files are:

## `fib5k.txt`

A text file of the first 5000 Fibonacci numbers, F(0) through F(4999).

This is for use in unit tests, such as in `test_functions.py`.

## `fib5k.hs`

A Haskell program currently used to (re)generate `fib5k.txt`. This is to
decrease the likelihood that the same bug would appear both in expected output
(gleaned from `fib5k.txt`) and in Python code being tested.

## `fib5k.md`

This file, explaining the `fib5k` files.

## Others

The three files described above are the only ones tracked in source control,
but if you compile `fib5k.hs`, you get `fib5k` or `fib5k.exe`, as well as
`fib5k.hi` and  `fib5k.o`.
