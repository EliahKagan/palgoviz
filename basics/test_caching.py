"""Tests for decorators in the caching module."""

# FIXME: Write unittest tests for @caching.memoize and @caching.memoize_by, at
# least as thorough as the doctests in caching.py. Make sure they pass (fix
# anything broken). Check that the doctests are replicated in test_caching.txt.
# Decide if any abridgements or other changes should be made to them in
# caching.py now that their main purpose is to document rather than test the
# code. If so, make the changes and make sure the modified doctests all pass.


# FIXME: @functools.cache, @caching.memoize, and @caching.memoize_by make
# caches that grow without bound: no matter how many entries are added to a
# cache and how much memory the cache uses, no entry is ever removed. To
# memoize a recursive algorithm to avoid recomputing subproblems, an unbounded
# cache is appropriate. But for other uses, often a bounded cache is needed
# instead. (Think of a web browser's cache.) Bounded caches are named for their
# invalidation policies: the rule for what entry is removed to make room for a
# new entry. (Invalidation is also called eviction.) Invalidation policies can
# involve complicated heuristics. But there are two popular policies that can
# be stated simply: least recently used (LRU), and least frequently used (LFU).
# When a new entry must be added to the cache, an LRU cache removes the least
# recently created/accessed entry, and it is the simplest bounded cache to
# implement efficiently, of those that are broadly useful.
#
# Please read the documentation for @functools.lru_cache, which is an LRU
# caching decorator, and try it out in a REPL or notebook. Such experimentation
# is likely to be time well spent, and may dramatically shorten the time these
# exercises take. Notice that the cache is bounded in a very straightforward
# way: by a maximum number of entries stored. Having come to understand what
# @functools.lru_cache does and how to use it, write tests in this module for
# your own LRU caching decorator implementations, @lru and @lru_di, that will
# go in caching.py. Their interfaces will be similar to, but not the same as,
# @functools.lru_cache. Interface differences common to @lru and @lru_di are:
#
# (1) Like @memoize and @memoize_by, @lru and @lru_di will only support unary
#     functions. (This limitation may be alleviated in a future problem set.)
#
# (2) @lru and @lru_di will have no default value for maxsize (which will still
#     be accepted as either a positional or keyword argument). Since maxsize
#     must always be specified, @lru and @lru_di are usable only as decorator
#     factories. They should raise an appropriate exception if maxsize is not a
#     strictly positive int. In particular, a maxsize of None is not allowed.
#
#     (In contrast, @functools.lru_cache(None) is allowed. It works just like
#     @functools.cache. It was the usual way to do decorator-based memoization
#     in Python before Python 3.9 added @functools.cache.)
#
# (3) @lru and @lru_di will not support a "typed" argument, nor otherwise
#     contain logic to support typed=True behavior.
#
# The "di" in @lru_di stands for "dependency injection." It, but not @lru, will
# accept an optional keyword-only argument specifying a factory that returns an
# initially empty mutable mapping when called with no arguments. In typical
# use, the mapping factory argument will be a mutable mapping type. If omitted,
# dict is used (it will be as if the dict type was passed). The cache may also
# use other data structures, but no other mappings; any functionality natural
# to do with a mapping shall be done by an instance returned by the mapping
# factory. Hence, the performance of @lru_di depends on the mapping type used.
#
# With mappings with O(1)-time operations, such as dict and mappings.HashTable,
# all @lru_di operations shall take O(1) time. That is, decorating a function
# definition with a caching.lru_di function-call expression increases the time
# it takes to define the function, and the time taken by each call to the
# function, by at most a constant; and in a cache hit (i.e., when the passed
# argument, and thus its return value, are in the cache already), the entire
# function call takes O(1) time. Since these times are amortized (rather than
# "strict") for dict and mappings.HashTable, that applies to the LRU cache too.
#
# @lru should not use dependency injection. But it cannot be implemented using
# @lru_di. Instead, write it in a substantially different (yet reasonable) way,
# taking advantage of some data structure that makes the implementation simple
# and elegant. @lru will most likely be easier and faster to implement than
# @lru_di; you can implement them in either order, but I recommend implementing
# @lru first. Either way, define @lru before @lru_di in caching.py.
#
# Most functionality of @lru and @lru_di overlaps. Test that functionality
# without duplicating test logic. To test the tests, you may want to use them
# to test @functools.lru_cache too, though this introduces a bit of additional
# complexity, since some of what @lru and @lru_di must be tested for differs
# from @functools.lru_cache (such as it being an error to call them without a
# maxsize argument or with a maxsize of None). Make sure to test all important
# behaviors of @lru and @lru_di including those not explicated here, as well as
# everything stated here even if not of vital importance. One exception: it is
# important that wrappers gain the metadata of the callables they wrap, but to
# simplify the exercise, it is optional to test it (unless you anticipate a
# bug, or one arises, in which case you should make sure tests cover that too).
# If you don't test this, include a to-do comment suggesting that it be done.
#
# Test @lru_di with no explicit mapping factory, and with at least dict and the
# UnsortedFlatTable, SortedFlatTable, BinarySearchTree, and HashTable types
# from our mappings module. Don't just test construction: all the tests should
# cover them all. Do this in a way that does not duplicate any test logic.
#
# @lru and @lru_di should also have doctests. They should be far less extensive
# than these unittest tests, serving mainly as documentation. Their docstrings
# should describe what they do and how to use them, sufficient for readers who
# already know what an LRU cache is. They should also either explain LRU caches
# or refer to an .md, .rst, or .ipynb file that does so. Feel free to adapt
# text from this comment. (Whether or not you do, still remove this comment
# when done. You can copy its text to another file if you want to retain it.)
#
# For @lru and @lru_di and their tests, I suggest using test-driven or
# test-first development, or some hybrid of the two, unless you strongly prefer
# to do otherwise. In particular, if you have trouble thinking of how to do it
# with all operations O(1), or how to make both @lru and @lru_di have all O(1)
# operations while still being written in substantially different ways from
# each other, I think writing tests early will help with that.
