#!/usr/bin/env python

"""Attempting data races on thread-safe and thread-unsafe singletons."""

__all__ = ['make_singleton', 'one_run', 'run_multiple', 'main']

import contextlib
import threading


def make_singleton(*, safe, spin_count):
    """Make a singleton class, optionally thread safe."""
    class Singleton:
        """Lazy implementation of the singleton pattern."""

        _instance = None
        _lock = threading.Lock() if safe else contextlib.nullcontext()

        def __new__(cls):
            with cls._lock:
                if cls._instance is None:
                    # Simulate nontrivial work to construct the instance.
                    for _ in range(spin_count):
                        pass

                    cls._instance = super().__new__(cls)

                return cls._instance

    return Singleton


class ThreeAttributes:
    start_time = None
    end_time = None
    s_instance = None


def one_run(*, safe, spin_count):
    """Run the data race test once."""
    Singleton = make_singleton(safe=safe, spin_count=spin_count)

    def set_singleton(storage):
        storage.s_instance = Singleton()

    thread1_storage = ThreeAttributes()
    thread2_storage = ThreeAttributes()

    t1 = threading.Thread(target=set_singleton, args=(thread1_storage,))
    t2 = threading.Thread(target=set_singleton, args=(thread2_storage,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert thread1_storage.s_instance is not None
    assert thread2_storage.s_instance is not None

    return thread1_storage.s_instance is thread2_storage.s_instance


def run_multiple(*, runs, safe, spin_count):
    """Run the data race test several times."""
    successes = sum(one_run(safe=safe, spin_count=spin_count)
                    for _ in range(runs))
    print(f'{successes} successful runs out of {runs}. {safe = }')


def main(*, runs=100, spin_count=1_500_000):
    """Run the test for both thread safe and thread unsafe."""
    run_multiple(runs=runs, safe=False, spin_count=spin_count)
    run_multiple(runs=runs, safe=True, spin_count=spin_count)


if __name__ == '__main__':
    main()
