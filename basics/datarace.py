#!/usr/bin/env python

"""Attempting data races on thread-safe and thread-unsafe singletons."""

__all__ = ['SPIN_COUNT', 'Singleton', 'main']

import threading

# Eventually we may adjust this to get ~10% collision rate in the unsafe demo.
SPIN_COUNT = 1_300_000


class Singleton:
    """Lazy implementation of the singleton pattern. Not thread-safe."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            # Simulate nontrivial work to construct the instance.
            for _ in range(SPIN_COUNT):
                pass

            cls._instance = super().__new__(cls)

        return cls._instance


def main():
    """Run the test."""

if __name__ == '__main__':
    main()
