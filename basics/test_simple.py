"""Tests for the simple functions in simple.py."""

import unittest

from simple import answer


class TestAnswer(unittest.TestCase):
    """Tests for the answer function."""

    __slots__ = ()

    def test_the_answer_is_42(self):
        result = answer()
        self.assertEqual(result, 42)

    def test_the_answer_is_an_int(self):
        result = answer()
        self.assertIsInstance(result, int)


if __name__ == '__main__':
    unittest.main()
