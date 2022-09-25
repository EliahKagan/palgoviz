#!/usr/bin/env python

"""Attempting data races on thread-safe and thread-unsafe singletons."""

__all__ = ['make_singleton', 'one_run', 'run_multiple', 'main']

import contextlib
import threading
import time


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


class Storage:
    pass


def one_run(*, safe, spin_count):
    """Run the data race test once."""
    Singleton = make_singleton(safe=safe, spin_count=spin_count)

    def set_singleton(storage):
        storage.start_time = time.perf_counter_ns()
        storage.instance = Singleton()
        storage.end_time = time.perf_counter_ns()

    storage1 = Storage()
    storage2 = Storage()

    thread1 = threading.Thread(target=set_singleton, args=(storage1,))
    thread2 = threading.Thread(target=set_singleton, args=(storage2,))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    return storage1, storage2


def run_multiple(*, runs, safe, spin_count):
    """Run the data race test several times."""

    successes = 0
    disjoints = 0
    confirmations = 0

    for _ in range(runs):
        storage1, storage2 = one_run(safe=safe, spin_count=spin_count)
        success = storage1.instance is storage2.instance
        disjoint = (storage1.end_time < storage2.start_time) or (storage2.end_time < storage1.start_time)
        confirmation = success is disjoint
        if success:
            successes += 1
        if disjoint:
            disjoints += 1
        if confirmation:
            confirmations += 1

    print(f'{safe=} {successes=} {disjoints=} {confirmations=} ({runs} runs)')


def main(*, runs=100, spin_count=1_500_000):
    """Run the test for both thread safe and thread unsafe."""
    run_multiple(runs=runs, safe=False, spin_count=spin_count)
    run_multiple(runs=runs, safe=True, spin_count=spin_count)


if __name__ == '__main__':
    main()
