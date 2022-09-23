#!/usr/bin/env python

"""Attempting data races on thread-safe and thread-unsafe singletons."""

__all__ = ['SPIN_COUNT', 'make_singleton', 'one_run', 'main']

import threading

# Eventually we may adjust this to get ~10% collision rate in the unsafe demo.
SPIN_COUNT = 1_300_000


def make_singleton(*, safe):
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

    if safe:
        Singleton()

    return Singleton


def one_run(*, safe):

    Singleton = make_singleton(safe=safe)

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

    return 1 if a is b else 0


def run_multiple(*, runs, safe):
    x = 0
    for _ in range(runs):
        x += one_run(safe=safe)

    print(f'{x} successful runs out of {runs}. {safe = }')


def main():
    """Run the test."""

    run_multiple(runs=100, safe=True)
    run_multiple(runs=100, safe=False)

if __name__ == '__main__':
    main()
