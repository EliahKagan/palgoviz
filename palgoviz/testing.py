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

"""
Test helpers used by code in the palgoviz package and/or notebooks.

If a test helper is not (meant to be) used outside the modules in tests/, but
it is used by multiple test modules or otherwise shouldn't be inside a "test_*"
module, then it should be in a non-public module in tests/, rather than here.
"""

__all__ = ['collect_if_not_ref_counting', 'ShortReprMeta']

import gc
import platform

if platform.python_implementation() == 'CPython':
    def collect_if_not_ref_counting():
        """Force a collection if we might not be using reference counting."""
        # CPython always refcounts as its primary GC strategy, so do nothing.
else:
    def collect_if_not_ref_counting():
        """Force a collection if we might not be using reference counting."""
        gc.collect()


class ShortReprMeta(type):
    """Metaclass to use class names as reprs, to improve doctest clarity."""

    def __repr__(self):
        """Represent a class as its bare name."""
        return self.__name__
