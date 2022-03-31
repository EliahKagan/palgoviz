"""
Types that compare in special ways.

The main use for this module is to help in building tests for code that sorts,
searches, or otherwise operates based on order comparisons, though it may have
other uses.
"""


class OrderIndistinct:
    """
    Objects indistinguishable by the "<" and ">" operators.

    OrderIndistinct instances compare for equality by their value attribute,
    but when that attribute differs, both "<" and ">" still return False.

    The purpose of this class is to help in testing sorts for stability.
    """
