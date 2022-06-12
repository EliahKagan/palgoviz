#!/usr/bin/env python

"""
Searching.

See also recursion.py.
"""

import bisect
import functools
import math
import operator


def _identity_function(arg):
    """Identity function. Return the argument unchanged."""
    return arg


def bsearch(values, x, key=None, reverse=False):
    """
    Binary search.

    Find the index of some y in values where neither x nor key(y) is lesser.
    Assume values is sorted as if by values.sort(key=key, reverse=reverse), but
    it may be of any sequence type (it need not be a list). If key is None or
    not passed, y is its own key: look for a y where neither x nor y is lesser.

    Time complexity is O(log n). Auxiliary space complexity is O(1). This
    implementation may be similar to one of your binary search implementations
    in recursion.py, but this supports an optional key selector, allows
    reverse-sorted input, and raises ValueError if the search finds no result.

    NOTE: I highly recommend NOT LOOKING at the binary search implementations
    in recursion.py (and not even their names and descriptions) while working
    this exercise. Usually it is very good to look at what you've already done,
    but I think this exercise will be much, MUCH more beneficial if you do not.

    [FIXME: After you are satisfied this solution is correct and all tests
    pass, review all your binary search implementations in recursion.py and
    replace this with a statement of which one this is similar to, if any. Also
    state, for each approach there that you didn't use here, if you could've
    used it here, why or why not, and, for any you could've used, any major
    advantages or disadvantages they would have, compared to what you did use.
    If an approach would require considerably more code, you should still
    consider it feasible... *if* you are convinced that it really can be done.]
    """
    if key is None:
        key = _identity_function
    compare = operator.gt if reverse else operator.lt

    low = 0
    high = len(values)

    while low < high:
        mid = (low + high) // 2
        mapped_key = key(values[mid])

        if compare(x, mapped_key):
            high = mid  # Go left.
        elif compare(mapped_key, x):
            low = mid + 1  # Go right.
        else:
            return mid

    raise ValueError(f'no item found with key similar to {x!r}')


def _ensure_not_reverse_comparing_instance(other):
    """Helper to make comparing two _ReverseComparing objects a hard error."""
    if isinstance(other, _ReverseComparing):
        raise TypeError('tried to compare two _ReverseComparing instances')


class _ReverseComparing:
    """
    Wrapper that holds an item, with reversed strict-order comparisons.

    This is an implementation detail of bsearch_alt. Other types should not try
    to implement "<", ">", "<=", or ">=" comparisons with _ReverseComparing.
    """

    __slots__ = ('item',)

    def __init__(self, item):
        self.item = item

    def __repr__(self):
        return f'{type(self).__name__}({self.item!r})'

    def __lt__(self, other):
        _ensure_not_reverse_comparing_instance(other)
        return other < self.item

    def __gt__(self, other):
        _ensure_not_reverse_comparing_instance(other)
        return other > self.item


def bsearch_alt(values, x, key=None, reverse=False):
    """
    Binary search, [FIXME: very briefly state how this function is different].

    This alternative implementation of bsearch must use a different technique.
    It has the same requirements, including restrictions on time and space. It
    should use the same approach as in one of the functions in recursion.py
    (but not the one, if any, whose approach bsearch uses above), unless that's
    not possible, as detailed in the text you added to the bsearch docstring.
    """
    if key is None:
        key = _identity_function

    x_for_bisect = (_ReverseComparing(x) if reverse else x)
    index = bisect.bisect_left(values, x_for_bisect, key=key)

    if index == len(values) or x_for_bisect < key(values[index]):
        raise ValueError(f'no item found with key similar to {x!r}')

    return index


# NOTE: first_satisfying, first_satisfying_iterative, and first_satisfying_good
#       can be worked in any order. Please read all their descriptions first.


def first_satisfying(predicate, low, high):
    """
    Find the first int satisfying a predicate that partitions the search space.

    The caller must ensure that there is some int k where low <= k < high and:

      - For every int i where low <= i < k, predicate(i) is falsy.
      - For every int j where k <= j < high, predicate(j) is truthy.

    That is, within the given bounds, if an argument is high enough to satisfy
    the predicate, increasing it continues to satisfy the predicate. This finds
    the lowest value high enough to satisfy the predicate (which is what k is).

    This implementation is recursive. It uses no library facilities besides
    builtins. Its time complexity is asymptotically optimal. [FIXME: Assume
    each call to predicate takes O(1) time. State the asymptotic time and
    auxiliary space complexities. Explain why it is that no asymptotically
    faster algorithm for this problem is possible, even in the absence of any
    restrictions on what techniques are used to implement it.]
    """
    # FIXME: Needs implementation.


def first_satisfying_iterative(predicate, low, high):
    """
    Find the first int satisfying a predicate that partitions the search space.

    This is like first_satisfying but iterative instead of recursive, also
    making no use of library facilities besides builtins. The algorithm is the
    same as, or very similar to, that algorithm. The code is even as close as
    it reasonably can be be to the code there, while still using no recursion.

    This has the same asymptotic time complexity as first_satisfying. Its
    auxiliary space complexity is [FIXME: state it asymptotically here].
    """
    # FIXME: Needs implementation.


def first_satisfying_good(predicate, low, high):
    """
    Find the first int satisfying a predicate that partitions the search space.

    This is like first_satisfying and first_satisfying_iterative, but with no
    restrictions on how it is implemented, except that it should make maximal
    use of standard library facilities to keep its own code simple and short.
    The actual code here will thus not resemble that of those two functions.

    This has the same asymptotic time complexity they do. Its auxiliary space
    complexity is [FIXME: state it asymptotically here].
    """
    # FIXME: Needs implementation.


def my_bisect_left(values, x, lo=0, hi=None, *, key=None, reverse=False):
    """
    Find the leftmost insertion point for a new key x in a sorted sequence.

    This is like bisect.bisect_left, except reverse-sorted input is supported
    (when reverse=True). Since it can be useful to pass lo and hi as keyword
    arguments, their names are retained for compatibility (instead of following
    the conventions elsewhere in this project and calling them low and high).

    Like bisect.bisect_left, the key function is applied to elements of values
    but not to x, and if key is not passed, every element is its own key.
    Assume values is sorted as if by values.sort(key=key, reverse=reverse).

    This uses no library functions but builtins. But it does use at least one
    function in this module, making it much shorter and simpler than otherwise.
    """
    # FIXME: Needs implementation.


def my_bisect_right(values, x, lo=0, hi=None, *, key=None, reverse=False):
    """
    Find the rightmost insertion point for a new key x in a sorted sequence.

    This is analogous to my_bisect_left, but for bisect.bisect_right. It has
    the same preconditions including how values comes sorted, and the same
    requirements on what functions it uses.
    """
    # FIXME: Needs implementation.


def two_sum_slow(numbers, total):
    """
    Find indices of two numbers that sum to total. Minimize auxiliary space.

    Although the numbers may be equal, the indices must be unequal. Give the
    left index before the right one. If there are multiple solutions, return
    any of them. If there are no solutions, raise ValueError.

    [FIXME: State the asymptotic time and auxiliary space complexities here.]
    """
    # Although un-Pythonic, this code avoids obscuring how the algorithm works.
    for left in range(len(numbers)):
        for right in range(left + 1, len(numbers)):
            if numbers[left] + numbers[right] == total:
                return left, right

    raise ValueError(f'no two numbers sum to {total!r}')


def two_sum_fast(numbers, total):
    """
    Find indices of two numbers that sum to total. Minimize running time.

    Although the numbers found may be equal, their indices must be unequal.
    Give the left index before the right one. If there are multiple solutions,
    return any of them. If there are no solutions, raise ValueError.

    [FIXME: State the asymptotic time and auxiliary space complexities here.]
    """
    history = {}

    for right, value in enumerate(numbers):
        try:
            left = history[total - value]
        except KeyError:
            history[right] = value
        else:
            return left, right

    raise ValueError(f'no two numbers sum to {total!r}')


def _two_sum_sorted_keyed(items, total, key):
    """Solve sorted 2-sum problem where map(key, items) are the numbers."""
    left = 0
    right = len(items) - 1

    while left < right:
        total_here = key(items[left]) + key(items[right])
        if total_here < total:
            left += 1
        elif total_here > total:
            right -= 1
        else:
            return left, right

    raise ValueError(f'no two numbers sum to {total!r}')


def two_sum_sorted(numbers, total):
    """
    Given sorted numbers, find indices of two numbers that sum to total.

    Minimize both running time and auxiliary space, to the extent possible.

    Although the numbers found may be equal, their indices must be unequal.
    Give the left index before the right one. If there are multiple solutions,
    return any of them. If there are no solutions, raise ValueError.

    [FIXME: State the asymptotic time and auxiliary space complexities here. If
    they are independently optimal, meaning this problem cannot be solved in
    asymptotically less time even with unlimited space, nor in asymptotically
    less space even in unlimited time, then say so and explain why. Otherwise,
    say why that cannot be done, and explain why you believe the tradeoff you
    picked between time and space is a reasonable choice.]
    """
    return _two_sum_sorted_keyed(numbers, total, lambda num: num)


def two_sum_nohash(numbers, total):
    """
    Find indices of two numbers that sum to total, without hashing.

    Minimize running time. If this and a previous function have substantial
    overlapping logic, extract it a nonpublic module-level function.

    Although the numbers found may be equal, their indices must be unequal.
    Give the left index before the right one. If there are multiple solutions,
    return any of them. If there are no solutions, raise ValueError.

    [FIXME: State the asymptotic time and auxiliary space complexities here.]
    """
    indices = sorted(range(len(numbers)), key=numbers.__getitem__)
    left, right = _two_sum_sorted_keyed(indices, total, numbers.__getitem__)
    return indices[left], indices[right]


def has_subset_sum_slow(numbers, total):
    """
    Check if any zero or more values in numbers sum to total.

    This is the subset sum decision problem. The name is misleading, as really
    the input represents a multiset (a.k.a. bag). The problem is to determine
    if any submultiset sums to the target total. So if a value appears k times
    in numbers, it may appear up to k times in a sum. All values are integers.

    This is a decision problem, so just return True or False. Algorithms that
    solve this can be adapted to solve the more useful problem of building and
    returning some "subset" that sums to the target, when there is one. Future
    exercises may cover that, together with more techniques for both versions.

    Although the input represents a multiset (so order doesn't matter), it is
    usually supplied as a sequence, and numbers is guaranteed to be a sequence
    here. You can, and probably should, rely on that in your solution.

    This implementation is recursive. It takes exponential time. It should
    sacrifice speed for simplicity, except that I do recommend avoiding
    unnecessary copying, in which case it will take O(2**len(numbers)) time.
    """
    def check(start, subtotal):
        if subtotal == 0:
            return True
        if start == len(numbers):
            return False
        return (check(start + 1, subtotal - numbers[start]) or
                check(start + 1, subtotal))

    return check(0, total)


def has_subset_sum(numbers, total):
    """
    Efficiently check if any zero or more values in numbers sum to total.

    This is the subset sum decision problem described in has_subset_sum_slow.
    This implementation is also recursive, resembling the implementation there,
    but much more efficient. This is fast enough for substantial problem sizes.

    [FIXME: Say something about this algorithm's asymptotic time complexity.]
    """
    memo = {}

    def check(start, subtotal):
        if subtotal == 0:
            return True
        if start == len(numbers):
            return False

        try:
            return memo[start, subtotal]
        except KeyError:
            result = memo[start, subtotal] = (
                check(start + 1, subtotal - numbers[start]) or
                check(start + 1, subtotal)
            )
            return result

    return check(0, total)


def has_subset_sum_alt(numbers, total):
    """
    Efficiently check if any zero or more values in numbers sum to total.

    This alternative implementation of has_subset_sum uses the same recursive
    algorithm (so it has the same asymptotic time complexity), but implements
    it using a substantially different technique. One implementation uses a
    previously created facility in another module of this project, or a similar
    facility in the standard library. The other does not use any such facility.

    FIXME: Unlike the standard library facility, the one in this project is
    cumbersome to use for problems like subset sum, due to a limitation that
    wasn't relevant in prior uses. Rename the existing version descriptively.
    Write a new version, appropriately generalized, that overcomes that
    limitation. (Give it the name your original implementation previously had.)
    """
    @functools.cache
    def check(start, subtotal):
        if subtotal == 0:
            return True
        if start == len(numbers):
            return False
        return (check(start + 1, subtotal - numbers[start]) or
                check(start + 1, subtotal))

    return check(0, total)


def count_coin_change_slow(coins, total):
    """
    Count how many ways to make change for a total with the coins.

    coins is a sequence of positive integer coin denominations, and total is a
    a positive integer amount for which change is to be made. All coins are
    available in unlimited quantities. A way to make change is a multiset of
    coins, so ways differing only in the order of the coins are the same way.
    So [5, 2, 2] and [2, 5, 2] are the same way to make change for 10, but they
    differ from [6, 1, 3].

    If the same value appears more than once in coins, they are distinct coin
    types happening to have the same value. So in a currency with a 1¢ piece, a
    2¢ piece portraying the king, and a 2¢ piece portraying the queen:

    >>> count_coin_change_slow([1, 2, 2], 5)
    6

    This implementation is recursive. It takes exponential time, sacrificing
    speed for simplicity other than avoiding unnecessary copying. It may
    resemble the solution to has_subset_sum_slow in other ways, too.
    """
    def count(start, subtotal):
        if subtotal == 0:
            return 1
        if start == len(coins):
            return 0
        return sum(count(start + 1, next_subtotal)
                   for next_subtotal in range(subtotal, -1, -coins[start]))

    return count(0, total)


def count_coin_change(coins, total):
    """
    Efficiently count how many ways to make change for a total with the coins.

    This is the coin change problem described in count_coin_change_slow. This
    implementation is also recursive, resembling the implementation there, but
    much more efficient. This function relates to count_coin_change_slow in the
    same way that has_subset_sum relates to has_subset_sum_slow.
    """
    memo = {}

    def count(start, subtotal):
        if subtotal == 0:
            return 1
        if start == len(coins):
            return 0

        try:
            return memo[start, subtotal]
        except KeyError:
            result = memo[start, subtotal] = sum(
                count(start + 1, next_subtotal)
                for next_subtotal in range(subtotal, -1, -coins[start])
            )
            return result

    return count(0, total)


def count_coin_change_alt(coins, total):
    """
    Efficiently count how many ways to make change for a total with the coins.

    This alternative implementation of count_coin_change uses the same
    recursive algorithm (so it has the same asymptotic time complexity), but
    implements it using a substantially different technique. This function
    relates to count_coin_change in the same way that has_subset_sum_alt
    relates to has_subset_sum.
    """
    @functools.cache
    def count(start, subtotal):
        if subtotal == 0:
            return 1
        if start == len(coins):
            return 0
        return sum(count(start + 1, next_subtotal)
                   for next_subtotal in range(subtotal, -1, -coins[start]))

    return count(0, total)


def can_escape_forest(forest, stamina, start_i, start_j, finish_i, finish_j):
    """
    Check if the tourist can escape the Scary Forest.

    The Scary Forest is a rectangular grid represented as a sequence of strings
    (rows) in which each square (character) is a tree ('*'), an empty spot of
    trail ('.'), or a flower whose species is abbreviated by a letter. The
    tourist starts at coordinates (start_i, start_j) and must get to their
    rocket ship at (finish_i, finish_j) by moves going north, south, east, or
    west. The tourist loses a unit of stamina per move, and will sleep forever
    when it runs out, except that reaching the rocket ship with zero stamina is
    okay, because being in a rocket ship is exciting enough to wake anybody up.

    If the tourist walks into a tree, the three swallows up the tourist, who
    will then live the rest of their life inside the tree. Also, the forest is
    suspended in an infinite abyss, so to walk out of it is to fall for all
    eternity. The other matter is that, while the tourist may step on a flower,
    this makes all flowers of that species angry, and it is a productive anger:
    they all immediately grow into trees once the tourist takes another step.

    Start and finish locations are guaranteed to be empty spots of trail ('.').
    Indexing is 0-based and uses matrix conventions: the i-coordinate increases
    to the south and the j-coordinate increases to the east. Tourists find that
    to be the scariest thing of all; that's why they named it the Scary Forest.

    >>> a = ('*A.B',
    ...      '..*.',
    ...      '*B.A')
    >>> can_escape_forest(a, 5, start_i=1, start_j=0, finish_i=1, finish_j=3)
    True
    >>> can_escape_forest(a, 4, start_i=1, start_j=0, finish_i=1, finish_j=3)
    False
    >>> can_escape_forest(a, 4, start_i=1, start_j=1, finish_i=1, finish_j=3)
    True
    >>> b = ('*A.A',
    ...      '..*.',
    ...      '*B.B')
    >>> can_escape_forest(b, 5, start_i=1, start_j=0, finish_i=1, finish_j=3)
    False
    >>> can_escape_forest(b, 10, start_i=1, start_j=0, finish_i=1, finish_j=3)
    False
    >>> c = ('.........*..A..',
    ...      'QQPP*BBAA*.*...',
    ...      'ABAB*PQRQ*.*.*B',
    ...      '....*........R.',
    ...      '****..***.****C',
    ...      '...*C*....D.P.D',
    ...      '**.....*C.....D')
    >>> can_escape_forest(c, 19, start_i=3, start_j=1, finish_i=3, finish_j=14)
    True
    >>> can_escape_forest(c, 18, start_i=3, start_j=1, finish_i=3, finish_j=14)
    False
    """
    grid = [list(row) for row in forest]
    angry_flowers = set()

    def on_board(i, j):
        return 0 <= i < len(grid) and 0 <= j < len(grid[i])

    def blocked(i, j):
        return grid[i][j] == '*' or grid[i][j] in angry_flowers

    def check(i, j, remaining_stamina):
        if i == finish_i and j == finish_j:
            return True

        if not on_board(i, j) or blocked(i, j) or remaining_stamina == 0:
            return False

        if grid[i][j] == '.':
            grid[i][j] = '*'
        else:
            angry_flowers.add(grid[i][j])

        neighbors = ((i, j - 1), (i, j + 1), (i - 1, j), (i + 1, j))
        result = any(check(h, k, remaining_stamina - 1) for h, k in neighbors)

        if grid[i][j] == '*':
            grid[i][j] = '.'
        else:
            angry_flowers.remove(grid[i][j])

        return result

    return check(start_i, start_j, stamina)


def _overestimate_escape_stamina(forest):
    """Compute an upper bound on the minimum stamina to escape a forest."""
    # The tourist can step on each empty spot and on a flower of each species.
    empty_trail_area = sum(row.count('.') for row in forest)
    species_count = len({ch for row in forest for ch in row if ch.isalpha()})
    return empty_trail_area + species_count


def min_forest_escape_stamina(forest, start_i, start_j, finish_i, finish_j):
    """
    Find the minimum stamina with which the tourist can escape the forest.

    Parameters mean the same as in can_escape_forest. If no amount of stamina
    is enough, return math.inf. One approach could be to call can_escape_forest
    with ascending stamina: 0, then 1, then 2, and so on (though you would have
    to figure out when to give up). That would find the right answer. On some
    inputs, it would even be the fastest way. But it would sometimes take too
    long. Use a different technique that is sometimes faster, even if sometimes
    slower. Reproduce at most very little logic from can_escape_forest (or its
    helpers). You can use anything from this project or the standard library.

    It's tempting to say this is a factor of [FIXME: give it in big-O] slower
    than can_escape_forest. But that's often not so, since [FIXME: explain why
    not, say something about what affects it, and give an example of a software
    engineering problem where this technique really does enjoy that guarantee].
    """
    def is_sufficient(stamina):
        return can_escape_forest(forest, stamina,
                                 start_i, start_j, finish_i, finish_j)

    upper_bound = _overestimate_escape_stamina(forest) + 1
    needed_stamina = first_satisfying(is_sufficient, 0, upper_bound)
    return math.inf if needed_stamina == upper_bound else needed_stamina


# TODO: Refactor this as a named tuple (namedtuple and inherit) after testing.
class _Pos:
    """Coordinates to a board square in Tread."""

    __slots__ = ('_i', '_j')

    def __init__(self, i, j):
        """Create a new player position with the specified coordinates."""
        self._i = i
        self._j = j

    def __repr__(self):
        """Representation for debugging, runnable as Python code."""
        return f'{type(self).__name__}({self.i!r}, {self.j!r})'

    def __str__(self):
        """Compact representation (not runnable as Python code)."""
        return f'{self.i},{self.j}'

    def __eq__(self, other):
        """Positions with equal corresponding coordinates are equal."""
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.i == other.i and self.j == other.j

    def __hash__(self):
        return hash((self.i, self.j))

    @property
    def i(self):
        """The i-coordinate (row index) of the position."""
        return self._i

    @property
    def j(self):
        """The j-coordinate (column index) of this position."""
        return self._j

    @property
    def neighbors(self):
        """Neighboring positions (but some might be off the board)."""
        yield _Pos(self.i, self.j - 1)
        yield _Pos(self.i, self.j + 1)
        yield _Pos(self.i - 1, self.j)
        yield _Pos(self.i + 1, self.j)


# TODO: Refactor this as a dataclass (via dataclass or attrs) after testing.
class _Player:
    """A player in Tread."""

    __slots__ = ('vis', 'old_pos', 'pos', 'gaffes')

    def __init__(self, start_i, start_j):
        """Create a new player with the specified starting coordinates."""
        self.vis = set()
        self.old_pos = _Pos(-1, -1)
        self.pos = _Pos(start_i, start_j)
        self.gaffes = 0

    def __repr__(self):
        """Representation for debugging. (Not runnable as Python code.)"""
        return (f'<{type(self).__name__}: vis={self.vis} '
                f'old_pos={self.old_pos} pos={self.pos} gaffes={self.gaffes}>')

    def is_blocking(self, pos):
        """Tell if a position is the current or the previous position."""
        return pos in (self.pos, self.old_pos)


class _Board:
    """Board geometry for a game of Tread."""

    __slots__ = ('_m', '_n', '_void')

    def __init__(self, m, n, vi, vj):
        """Create an m-by-n board whose void is at (vi, vj)."""
        self._m = m
        self._n = n
        self._void = _Pos(vi, vj)

    def __repr__(self):
        """Representation for debugging, runnable as Python code."""
        return (f'{type(self).__name__}({self._m!r}, {self._n!r},'
                f' {self._void.i!r}, {self._void.j!r})')

    def __contains__(self, pos):
        """Tell if a position is on the board (in bounds and not the void)."""
        return (0 <= pos.i < self._m and 0 <= pos.j < self._n
                and pos != self._void)


_MAX_GAFFES = 2
"""The maximum number of gaffes allowed to each player in a game of Tread."""


def _active_player_has_winning_strategy(board, active, inactive):
    """Tell if the active Tread player has a winning strategy in mid-game."""
    # If Inactive's move was illegal, Active calls it out and immediately wins.
    if (inactive.pos not in board or active.is_blocking(active.pos) or
            (inactive.pos in inactive.vis and inactive.gaffes == _MAX_GAFFES)):
        return True

    # Active ensures that Inactive's current and future gaffes are detected.
    gaffe = inactive.pos in inactive.vis
    if gaffe:
        inactive.gaffes += 1
    else:
        inactive.vis.add(inactive.pos)

    # Record Active's current and old position so we can backtrack the game.
    old_old_pos = active.old_pos
    active.old_pos = active.pos

    try:
        for pos in active.old_pos.neighbors:
            active.pos = pos
            if not _active_player_has_winning_strategy(board, inactive, active):
                return True  # Active can deny Inactive a winning strategy.

        return False  # Active has no way to deny Inactive a winning strategy.
    finally:
        # Restore Active's current and old position, to backtrack the game.
        active.pos = active.old_pos
        active.old_pos = old_old_pos

        # Restore Inactive's gaffe bookkeeping too. (Active is honorable.)
        if gaffe:
            inactive.gaffes -= 1
        else:
            inactive.vis.remove(inactive.pos)


def find_tread_winner(m, n, vi, vj, ai, aj, bi, bj):
    """
    Determine which player, A or B, has a winning strategy in a game of Tread.

    A player has a winning strategy if, provided they play perfectly, they are
    guaranteed to win, no matter how their opponent plays.

    A game of Tread is played on an m-by-n board with a void at (vi, vj) where
    no one can go. A starts at (ai, aj), B at (bi, bj). Players alternate
    turns. A goes first. The player whose turn it is must move up, down, left,
    or right on the board, but can't move to the void, their opponent's
    location, or their opponent's most recent previous location. Also, to move
    onto any square one has ever previously occupied is a gaffe; each player is
    allowed at most two gaffes. If a player has no legal move, their opponent
    wins. The void and players' start squares are guaranteed to be three
    different squares within the m-by-n rectangle.

    Return 'A' if A has a winning strategy, or 'B' if B has a winning strategy.
    Some player is guaranteed to have one, because [FIXME: Say why.]

    Use the simplest correct algorithm you can think of that passes all tests
    reasonably fast. But the code itself may be short or long and may use any
    combination of language features. It should be correct and easy to read.
    You might want to make and use helper functions/classes.

    >>> find_tread_winner(1, 3, 0, 0, 0, 1, 0, 2)
    'A'
    """
    board = _Board(m, n, vi, vj)
    a = _Player(ai, aj)
    b = _Player(bi, bj)
    return 'A' if _active_player_has_winning_strategy(board, a, b) else 'B'


if __name__ == '__main__':
    import doctest
    doctest.testmod()
