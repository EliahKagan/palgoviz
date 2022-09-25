#!/usr/bin/env python

"""Attempting data races on thread-safe and thread-unsafe singletons."""

__all__ = ['make_singleton', 'one_run', 'run_multiple', 'main']

import threading


# TODO: Have the thread-safe Singleton implementation do it via locking.
def make_singleton(*, safe, spin_count):
    """Make a singleton class, optionally thread safe."""
    class Singleton:
        """Lazy implementation of the singleton pattern."""

        _instance = None

        def __new__(cls):
            if cls._instance is None:
                # Simulate nontrivial work to construct the instance.
                for _ in range(spin_count):
                    pass

                cls._instance = super().__new__(cls)

            return cls._instance

    if safe:
        Singleton()

    return Singleton


def one_run(*, safe, spin_count):
    """Run the data race test once."""
    Singleton = make_singleton(safe=safe, spin_count=spin_count)

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

    return a is b


def run_multiple(*, runs, safe, spin_count):
    """Run the data race test several times."""
    successes = sum(one_run(safe=safe, spin_count=spin_count)
                    for _ in range(runs))
    print(f'{successes} successful runs out of {runs}. {safe = }')


def main(*, runs=100, spin_count=1_300_000):
    """Run the test for both thread safe and thread unsafe."""
    run_multiple(runs=runs, safe=True, spin_count=spin_count)
    run_multiple(runs=runs, safe=False, spin_count=spin_count)


if __name__ == '__main__':
    main()
