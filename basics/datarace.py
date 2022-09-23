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

    a = None
    b = None

    def set_a():
        nonlocal a
        a = Singleton()

    def set_b():
        nonlocal b
        b = Singleton()

    t1 = threading.Thread(target=set_a)
    t2 = threading.Thread(target=set_b)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert a is not None
    assert b is not None

    print(a is b)


if __name__ == '__main__':
    main()
