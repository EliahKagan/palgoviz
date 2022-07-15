import unittest


from adders import make_adder, Adder

class TestMakeAdder(unittest.TestCase):

    # Test adds to argument when assigned (int)
    def test_adds_7_and_4_correctly(self):
        f = make_adder(7)
        self.assertEqual(f(4), 11)

    def test_adds_7_and_10_correctly(self):
        f = make_adder(7)
        self.assertEqual(f(10), 17)

    # Test adds to argument no assignment (int)
    def test_adds_6_and_2_no_assignment(self):
        self.assertEqual(make_adder(6)(2), 8)

    # Test adds to argument (string)
    def test_adds_cat_and_dog_correctly(self):
        s = make_adder('cat')
        self.assertEqual(s(' dog'), 'cat dog')


class TestAdder(unittest.TestCase):

    # Test adds to argument when assigned (int)
    def test_adds_7_and_4_correctly(self):
        a = Adder(7)
        self.assertEqual(a(4), 11)

    def test_adds_7_and_10_correctly(self):
        a = Adder(7)
        self.assertEqual(a(10), 17)

    # Test adds to argument no assignment (int)
    def test_adds_6_and_2_correctly(self):
        self.assertEqual(Adder(6)(2), 8)

    # Test adds to argument (string)
    def test_adds_cat_and_dog_correctly(self):
        u = Adder('cat')
        self.assertEqual(u(' dog'), 'cat dog')

    # Test both equality comparison and hashability
    def test_equal_sets_compare_equal(self):
        lhs = {Adder(7), Adder(7), Adder(6), Adder(7.0)}
        rhs = {Adder(6), Adder(7)}
        self.assertTrue(lhs == rhs)

    # Test can access left_addend
    def test_can_access_left_addend_and_it_is_correct(self):
        a = Adder(7)
        self.assertEqual(a.left_addend, 7)

    # Test can't assign left_addend
    def test_cannot_assign_left_addend(self):
        a = Adder(7)
        with self.assertRaises(AttributeError):
            a.left_addend = 8

    # Test can't add new attributes
    def test_cannot_assign_new_attributes(self):
        a = Adder(7)
        with self.assertRaises(AttributeError):
            a.right_addend = 5