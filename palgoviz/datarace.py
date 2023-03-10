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

"""Attempting data races on thread safe and thread unsafe singletons."""

__all__ = ['make_singleton', 'one_run', 'run_multiple', 'main']

import contextlib
import threading
import time
import types


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


def one_run(*, safe, spin_count):
    """Run the data race test once."""
    Singleton = make_singleton(safe=safe, spin_count=spin_count)

    def set_singleton(storage):
        storage.start_time = time.perf_counter_ns()
        storage.instance = Singleton()
        storage.end_time = time.perf_counter_ns()

    storage1 = types.SimpleNamespace()
    storage2 = types.SimpleNamespace()

    thread1 = threading.Thread(target=set_singleton, args=(storage1,))
    thread2 = threading.Thread(target=set_singleton, args=(storage2,))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    return storage1, storage2


def run_multiple(*, runs, safe, spin_count):
    """
    Run the data race test several times and collect the results.

    This tests the hypothesis that creation of a unique singleton instance
    succeeds if and only if the time intervals of the calls to Singleton on
    separate threads are disjoint. This hypothesis is shown to be true (in
    cases tested) for the thread unsafe version. It is false for the thread
    safe version, which is good, since we want the thread safe version to
    always succeed.
    """

    successes = 0
    disjoints = 0
    confirmations = 0

    for _ in range(runs):
        storage1, storage2 = one_run(safe=safe, spin_count=spin_count)
        success = storage1.instance is storage2.instance
        disjoint = (storage1.end_time < storage2.start_time or
                    storage2.end_time < storage1.start_time)
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
