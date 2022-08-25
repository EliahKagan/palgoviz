#!/usr/bin/env python

"""Tests for the functions in recursion.py."""

from abc import ABC, abstractmethod
import bisect
import unittest

from parameterized import parameterized, parameterized_class

from compare import OrderIndistinct, Patient, WeakDiamond

from recursion import (
    insort_left_linear,
    insort_right_linear,
    merge_sort,
    merge_sort_bottom_up,
    merge_sort_bottom_up_unstable,
    merge_two,
    merge_two_alt,
    merge_two_slow,
    bst_count,
    bst_count_iterative,
)

_NORTH = WeakDiamond.NORTH
_SOUTH = WeakDiamond.SOUTH
_EAST = WeakDiamond.EAST
_WEST = WeakDiamond.WEST


def _build_insort_test_parameters(expected):
    """
    Build insort test cases: old items (as tuple), new item, expected result.

    The old items are given as a tuple so that each run of a test that uses
    them has to make a new list from it. Otherwise tests might contaminate each
    other (and also, even if not, debugging would be hard).
    """
    return [(tuple(expected[:index] + expected[index + 1:]), item, expected)
            for index, item in enumerate(expected)]


class TestInsortAbstract(ABC, unittest.TestCase):
    """Shared tests for insort_left_linear and insert_right_linear."""

    @property
    @abstractmethod
    def implementation(self):
        """The search-and-insert function under test."""

    def test_item_put_into_empty_list(self):
        sorted_items = []
        self.implementation(sorted_items, 42)
        self.assertListEqual(sorted_items, [42])

    def test_low_item_put_in_front_of_singleton_list(self):
        sorted_items = [76]
        self.implementation(sorted_items, 42)
        self.assertListEqual(sorted_items, [42, 76])

    def test_high_item_put_in_back_of_singleton_list(self):
        sorted_items = [42]
        self.implementation(sorted_items, 76)
        self.assertListEqual(sorted_items, [42, 76])

    def test_low_item_put_before_two(self):
        sorted_items = ['B', 'D']
        self.implementation(sorted_items, 'A')
        self.assertListEqual(sorted_items, ['A', 'B', 'D'])

    def test_medium_item_put_between_two(self):
        sorted_items = ['B', 'D']
        self.implementation(sorted_items, 'C')
        self.assertListEqual(sorted_items, ['B', 'C', 'D'])

    def test_high_item_put_after_two(self):
        sorted_items = ['B', 'D']
        self.implementation(sorted_items, 'E')
        self.assertListEqual(sorted_items, ['B', 'D', 'E'])

    def test_lowest_item_put_leftmost_in_three(self):
        sorted_items = [12.3, 45.6, 78.9]
        self.implementation(sorted_items, 0.1)
        self.assertListEqual(sorted_items, [0.1, 12.3, 45.6, 78.9])

    def test_medium_low_item_put_mid_left_in_three(self):
        sorted_items = [12.3, 45.6, 78.9]
        self.implementation(sorted_items, 31.8)
        self.assertListEqual(sorted_items, [12.3, 31.8, 45.6, 78.9])

    def test_medium_high_item_put_mid_right_in_three(self):
        sorted_items = [12.3, 45.6, 78.9]
        self.implementation(sorted_items, 62.7)
        self.assertListEqual(sorted_items, [12.3, 45.6, 62.7, 78.9])

    def test_highest_item_put_rightmost_in_three(self):
        sorted_items = [12.3, 45.6, 78.9]
        self.implementation(sorted_items, 110.2)
        self.assertListEqual(sorted_items, [12.3, 45.6, 78.9, 110.2])

    _NUMBERS = [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315, 5660]

    _WORDS = ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux', 'spam']

    @parameterized.expand(_build_insort_test_parameters(_NUMBERS)
                          + _build_insort_test_parameters(_WORDS))
    def test_new_item_put_in_order_in_several(self, olds, new, expected):
        sorted_items = list(olds)
        self.implementation(sorted_items, new)
        self.assertListEqual(sorted_items, expected)

    @parameterized.expand([
        (range(1, 101), 12, [*range(1, 13), *range(12, 101)]),
        (range(1, 101), 15, [*range(1, 16), *range(15, 101)]),
        (range(1, 101), 79, [*range(1, 80), *range(79, 101)]),
        (range(1, 101), 82, [*range(1, 83), *range(82, 101)]),
    ])
    def test_duplicate_item_put_in_order_in_hundred(self, olds, new, expected):
        sorted_items = list(olds)
        self.implementation(sorted_items, new)
        self.assertListEqual(sorted_items, expected)


class TestInsortLeftAbstract(TestInsortAbstract):
    """Tests for leftmost-point insort functions."""

    def test_incomparable_put_first(self):
        sorted_items = [
            OrderIndistinct(1), OrderIndistinct(2), OrderIndistinct(3),
            OrderIndistinct(4), OrderIndistinct(5),
        ]

        expected = [
            OrderIndistinct(6), OrderIndistinct(1), OrderIndistinct(2),
            OrderIndistinct(3), OrderIndistinct(4), OrderIndistinct(5),
        ]

        self.implementation(sorted_items, OrderIndistinct(6))
        self.assertListEqual(sorted_items, expected)

    @parameterized.expand([
        ((_SOUTH, _EAST, _WEST, _NORTH), _EAST,
            [_SOUTH, _EAST, _EAST, _WEST, _NORTH]),
        ((_SOUTH, _EAST, _WEST, _NORTH), _WEST,
            [_SOUTH, _WEST, _EAST, _WEST, _NORTH]),
        ((_SOUTH, _WEST, _EAST, _NORTH), _EAST,
            [_SOUTH, _EAST, _WEST, _EAST, _NORTH]),
        ((_SOUTH, _WEST, _EAST, _NORTH), _WEST,
            [_SOUTH, _WEST, _WEST, _EAST, _NORTH]),
    ])
    def test_new_weak_item_put_in_order_leftward(self, olds, new, expected):
        sorted_items = list(olds)
        self.implementation(sorted_items, new)
        self.assertListEqual(sorted_items, expected)

    def test_weak_ordered_item_put_left_of_multiple_similars(self):
        sorted_items = [Patient('A', 1), Patient('Z', 2), Patient('B', 3),
                        Patient('Y', 3), Patient('C', 3), Patient('X', 4)]

        new_item = Patient('N', 3)

        expected = sorted_items[:]
        expected.insert(2, new_item)  # It should go at the LEFT of the range.

        self.implementation(sorted_items, new_item)
        self.assertListEqual(sorted_items, expected)


class TestInsortRightAbstract(TestInsortAbstract):
    """Tests for rightmost-point insort functions."""

    def test_incomparable_put_last(self):
        sorted_items = [
            OrderIndistinct(1), OrderIndistinct(2), OrderIndistinct(3),
            OrderIndistinct(4), OrderIndistinct(5),
        ]

        expected = [
            OrderIndistinct(1), OrderIndistinct(2), OrderIndistinct(3),
            OrderIndistinct(4), OrderIndistinct(5), OrderIndistinct(6),
        ]

        self.implementation(sorted_items, OrderIndistinct(6))
        self.assertListEqual(sorted_items, expected)

    @parameterized.expand([
        ((_SOUTH, _EAST, _WEST, _NORTH), _EAST,
            [_SOUTH, _EAST, _WEST, _EAST, _NORTH]),
        ((_SOUTH, _EAST, _WEST, _NORTH), _WEST,
            [_SOUTH, _EAST, _WEST, _WEST, _NORTH]),
        ((_SOUTH, _WEST, _EAST, _NORTH), _EAST,
            [_SOUTH, _WEST, _EAST, _EAST, _NORTH]),
        ((_SOUTH, _WEST, _EAST, _NORTH), _WEST,
            [_SOUTH, _WEST, _EAST, _WEST, _NORTH]),
    ])
    def test_new_weak_item_put_in_order_rightward(self, olds, new, expected):
        sorted_items = list(olds)
        self.implementation(sorted_items, new)
        self.assertListEqual(sorted_items, expected)

    def test_weak_ordered_item_put_right_of_multiple_similars(self):
        sorted_items = [Patient('A', 1), Patient('Z', 2), Patient('B', 3),
                        Patient('Y', 3), Patient('C', 3), Patient('X', 4)]

        new_item = Patient('N', 3)

        expected = sorted_items[:]
        expected.insert(5, new_item)  # It should go at the RIGHT of the range.

        self.implementation(sorted_items, new_item)
        self.assertListEqual(sorted_items, expected)


class TestInsortLeft(TestInsortLeftAbstract):
    """Tests for bisect.insort_left. This is really to test our tests."""

    @property
    def implementation(self):
        return bisect.insort_left


class TestInsortRight(TestInsortRightAbstract):
    """Tests for bisect.insort_right. This is really to test our tests."""

    @property
    def implementation(self):
        return bisect.insort_right


# TODO: Test which, and how many, and what kind, of comparisons are performed.
class TestInsortLeftLinear(TestInsortLeftAbstract):
    """Tests for the insort_left_linear function."""

    @property
    def implementation(self):
        return insort_left_linear


# TODO: Test which, and how many, and what kind, of comparisons are performed.
class TestInsortRightLinear(TestInsortRightAbstract):
    """Tests for the insort_right_linear function."""

    @property
    def implementation(self):
        return insort_right_linear


del TestInsortAbstract, TestInsortLeftAbstract, TestInsortRightAbstract


@parameterized_class(('name', 'function'), [
    (merge_two_slow.__name__, staticmethod(merge_two_slow)),
    (merge_two.__name__, staticmethod(merge_two)),
    (merge_two_alt.__name__, staticmethod(merge_two_alt)),
])
class TestTwoWayMergers(unittest.TestCase):
    """Tests for the two way merge functions."""

    def test_left_first_interleaved_merges(self):
        result = self.function([1, 3, 5], [2, 4, 6])
        self.assertListEqual(result, [1, 2, 3, 4, 5, 6])

    def test_left_first_and_last_interleaved_merges(self):
        result = self.function([1, 3, 7], [2, 4, 6])
        self.assertListEqual(result, [1, 2, 3, 4, 6, 7])

    def test_right_first_interleaved_merges(self):
        result = self.function([2, 4, 6], [1, 3, 5])
        self.assertListEqual(result, [1, 2, 3, 4, 5, 6])

    def test_right_first_and_last_interleaved_merges(self):
        result = self.function([2, 4, 6], [1, 3, 7])
        self.assertListEqual(result, [1, 2, 3, 4, 6, 7])

    def test_empty_list_on_left_gives_right_side(self):
        result = self.function([], [2, 4, 6])
        self.assertListEqual(result, [2, 4, 6])

    def test_empty_tuple_on_left_gives_right_side(self):
        result = self.function((), [2, 4, 6])
        self.assertListEqual(result, [2, 4, 6])

    def test_empty_tuple_with_empty_list_gives_empty_list(self):
        result = self.function((), [])
        self.assertListEqual(result, [])

    def test_empty_list_with_empty_tuple_gives_empty_list(self):
        result = self.function([], ())
        self.assertListEqual(result, [])

    def test_empty_tuple_on_left_gives_right_side_as_list(self):
        """
        Merging an empty tuple with a tuple with duplicate leading items works.
        """
        result = self.function((), (1, 1, 4, 7, 8))
        self.assertListEqual(result, [1, 1, 4, 7, 8])

    def test_empty_tuple_on_right_gives_left_side_as_list(self):
        """
        Merging a tuple with duplicate leading items with an empty tuple works.
        """
        result = self.function((1, 1, 4, 7, 8), ())
        self.assertListEqual(result, [1, 1, 4, 7, 8])

    def test_is_a_stable_merge_when_items_do_not_compare(self):
        lhs = [OrderIndistinct(1), OrderIndistinct(2), OrderIndistinct(3)]
        rhs = [OrderIndistinct(4), OrderIndistinct(5), OrderIndistinct(6)]
        expected = [OrderIndistinct(1), OrderIndistinct(2), OrderIndistinct(3),
                    OrderIndistinct(4), OrderIndistinct(5), OrderIndistinct(6)]
        result = self.function(lhs, rhs)
        self.assertListEqual(result, expected)

    def test_is_a_stable_merge_when_items_compare_equal(self):
        lhs = 1
        rhs = 1.0
        r1, r2 = self.function((lhs,), (rhs,))
        with self.subTest(result='r1'):
            self.assertIs(r1, lhs)
        with self.subTest(result='r2'):
            self.assertIs(r2, rhs)

    def test_is_a_stable_merge_when_some_items_compare_equal(self):
        lhs = [WeakDiamond.SOUTH, WeakDiamond.EAST, WeakDiamond.NORTH]
        rhs = [WeakDiamond.WEST, WeakDiamond.WEST]
        expected = [WeakDiamond.SOUTH, WeakDiamond.EAST, WeakDiamond.WEST,
                    WeakDiamond.WEST, WeakDiamond.NORTH]
        result = self.function(lhs, rhs)
        self.assertListEqual(result, expected)


_SORT_PARAMS = [
    (merge_sort.__name__,
        staticmethod(merge_sort)),
    (merge_sort_bottom_up_unstable.__name__,
        staticmethod(merge_sort_bottom_up_unstable)),
    (merge_sort_bottom_up.__name__,
        staticmethod(merge_sort_bottom_up)),
]

_MERGE_PARAMS = [
    ('no_args', dict()),
    (merge_two_slow.__name__, dict(merge=merge_two_slow)),
    (merge_two.__name__, dict(merge=merge_two)),
    (merge_two_alt.__name__, dict(merge=merge_two_alt)),
]

_COMBINED_PARAMS = [(f'{sort_name}_{merge_name}', sort, kwargs)
                    for sort_name, sort in _SORT_PARAMS
                    for merge_name, kwargs in _MERGE_PARAMS]


@parameterized_class(('label', 'sort', 'kwargs'), _COMBINED_PARAMS)
class TestMergeSort(unittest.TestCase):
    """Tests for the merge sort functions."""

    def test_empty_list_sorts(self):
        result = self.sort([], **self.kwargs)
        self.assertListEqual(result, [])

    def test_empty_tuple_sorts(self):
        result = self.sort((), **self.kwargs)
        self.assertListEqual(result, [])

    def test_singleton_sorts(self):
        result = self.sort((2,), **self.kwargs)
        self.assertListEqual(result, [2])

    def test_two_element_sorted_list_is_unchanged(self):
        result = self.sort([10, 20], **self.kwargs)
        self.assertListEqual(result, [10, 20])

    def test_two_element_unsorted_list_is_sorted(self):
        result = self.sort([20, 10], **self.kwargs)
        self.assertListEqual(result, [10, 20])

    def test_two_element_equal_list_is_unchanged(self):
        result = self.sort([3, 3], **self.kwargs)
        self.assertListEqual(result, [3, 3])

    def test_several_ints_are_sorted(self):
        vals = [5660, -6307, 5315, 389, 3446, 2673, 1555, -7225, 1597, -7129]
        expected = [-7225, -7129, -6307, 389, 1555, 1597, 2673, 3446, 5315,
                    5660]
        result = self.sort(vals, **self.kwargs)
        self.assertListEqual(result, expected)

    def test_several_strings_are_sorted(self):
        vals = ['foo', 'bar', 'baz', 'quux', 'foobar', 'ham', 'spam', 'eggs']
        expected = ['bar', 'baz', 'eggs', 'foo', 'foobar', 'ham', 'quux',
                    'spam']
        result = self.sort(vals, **self.kwargs)
        self.assertListEqual(result, expected)


_STABLE_SORT_PARAMS = [
    (merge_sort.__name__,
        staticmethod(merge_sort)),
    (merge_sort_bottom_up.__name__,
        staticmethod(merge_sort_bottom_up)),
]

_STABLE_COMBINED_PARAMS = [(f'{sort_name}_{merge_name}', sort, kwargs)
                           for sort_name, sort in _STABLE_SORT_PARAMS
                           for merge_name, kwargs in _MERGE_PARAMS]


@parameterized_class(('label', 'sort', 'kwargs'), _STABLE_COMBINED_PARAMS)
class TestMergeSortStability(unittest.TestCase):
    """Tests that the merge sort functions intended to be stable are stable."""

    def test_sort_is_stable(self):
        vals = [0.0, 0, False]
        results = self.sort(vals, **self.kwargs)
        for i, (val, result) in enumerate(zip(vals, results)):
            with self.subTest(index=i):
                self.assertIs(result, val)

    def test_sort_is_stable_with_100_items(self):
        vals = [OrderIndistinct(x) for x in range(100)]
        result = self.sort(vals, **self.kwargs)
        self.assertListEqual(result, vals)


@parameterized_class(('label', 'implementation'), [
    (bst_count.__name__, staticmethod(bst_count)),
    (bst_count_iterative.__name__, staticmethod(bst_count_iterative)),
])
class TestBstCount(unittest.TestCase):
    """Tests for the bst_count and bst_count_iterative functions."""

    @parameterized.expand([
        ('n0', 0, 1),
        ('n1', 1, 1),
        ('n2', 2, 2),
        ('n3', 3, 5),
        ('n4', 4, 14),
        ('n5', 5, 42),
        ('n6', 6, 132),
        ('n7', 7, 429),
        ('n8', 8, 1430),
        ('n9', 9, 4862),
        ('n10', 10, 16796),
        ('n11', 11, 58786),
        ('n12', 12, 208012),
        ('n13', 13, 742900),
        ('n14', 14, 2674440),
        ('n15', 15, 9694845),
        ('n16', 16, 35357670),
        ('n17', 17, 129644790),
        ('n18', 18, 477638700),
        ('n19', 19, 1767263190),
        ('n20', 20, 6564120420),
        ('n21', 21, 24466267020),
        ('n22', 22, 91482563640),
        ('n23', 23, 343059613650),
        ('n24', 24, 1289904147324),
        ('n25', 25, 4861946401452),
        ('n26', 26, 18367353072152),
        ('n27', 27, 69533550916004),
        ('n28', 28, 263747951750360),
        ('n29', 29, 1002242216651368),
        ('n30', 30, 3814986502092304),
        ('n31', 31, 14544636039226909),
        ('n32', 32, 55534064877048198),
        ('n33', 33, 212336130412243110),
        ('n34', 34, 812944042149730764),
        ('n35', 35, 3116285494907301262),
        ('n36', 36, 11959798385860453492),
        ('n37', 37, 45950804324621742364),
        ('n38', 38, 176733862787006701400),
        ('n39', 39, 680425371729975800390),
        ('n40', 40, 2622127042276492108820),
        ('n41', 41, 10113918591637898134020),
        ('n42', 42, 39044429911904443959240),
        ('n43', 43, 150853479205085351660700),
        ('n44', 44, 583300119592996693088040),
        ('n45', 45, 2257117854077248073253720),
        ('n46', 46, 8740328711533173390046320),
        ('n47', 47, 33868773757191046886429490),
        ('n48', 48, 131327898242169365477991900),
        ('n49', 49, 509552245179617138054608572),
        ('n50', 50, 1978261657756160653623774456),
        ('n51', 51, 7684785670514316385230816156),
        ('n52', 52, 29869166945772625950142417512),
        ('n53', 53, 116157871455782434250553845880),
        ('n54', 54, 451959718027953471447609509424),
        ('n55', 55, 1759414616608818870992479875972),
        ('n56', 56, 6852456927844873497549658464312),
        ('n57', 57, 26700952856774851904245220912664),
        ('n58', 58, 104088460289122304033498318812080),
        ('n59', 59, 405944995127576985730643443367112),
        ('n60', 60, 1583850964596120042686772779038896),
        ('n61', 61, 6182127958584855650487080847216336),
        ('n62', 62, 24139737743045626825711458546273312),
        ('n63', 63, 94295850558771979787935384946380125),
        ('n64', 64, 368479169875816659479009042713546950),
        ('n65', 65, 1440418573150919668872489894243865350),
        ('n66', 66, 5632681584560312734993915705849145100),
        ('n67', 67, 22033725021956517463358552614056949950),
        ('n68', 68, 86218923998960285726185640663701108500),
        ('n69', 69, 337485502510215975556783793455058624700),
        ('n70', 70, 1321422108420282270489942177190229544600),
        ('n71', 71, 5175569924646105559418940193995065716350),
        ('n72', 72, 20276890389709399862928998568254641025700),
        ('n73', 73, 79463489365077377841208237632349268884500),
        ('n74', 74, 311496878311103321137536291518809134027240),
        ('n75', 75, 1221395654430378811828760722007962130791020),
        ('n76', 76, 4790408930363303911328386208394864461024520),
        ('n77', 77, 18793142726809884575211361279087545193250040),
        ('n78', 78, 73745243611532458459690151854647329239335600),
        ('n79', 79, 289450081175264899454283846029490767264392230),
        ('n80', 80, 1136359577947336271931632877004667456667613940),
        ('n81', 81, 4462290049988320482463241297506133183499654740),
        ('n82', 82, 17526585015616776834735140517915655636396234280),
        ('n83', 83, 68854441132780194707888052034668647142985206100),
        ('n84', 84, 270557451039395118028642463289168566420671280440),
        ('n85', 85, 1063353702922273835973036658043476458723103404520),
        ('n86', 86, 4180080073556524734514695828170907458428751314320),
        ('n87', 87, 16435314834665426797069144960762886143367590394940),
        ('n88', 88, 64633260585762914370496637486146181462681535261000),
        ('n89', 89, 254224158304000796523953440778841647086547372026600),
        ('n90', 90, 1000134600800354781929399250536541864362461089950800),
        ('n91', 91, 3935312233584004685417853572763349509774031680023800),
        ('n92', 92, 15487357822491889407128326963778343232013931127835600),
        ('n93', 93, 60960876535340415751462563580829648891969728907438000),
        ('n94', 94, 239993345518077005168915776623476723006280827488229600),
        ('n95', 95, 944973797977428207852605870454939596837230758234904050),
        ('n96', 96, 3721443204405954385563870541379246659709506697378694300),
        ('n97', 97, 14657929356129575437016877846657032761712954950899755100),
        ('n98', 98, 57743358069601357782187700608042856334020731624756611000),
        ('n99', 99, 227508830794229349661819540395688853956041682601541047340),
        ('n100', 100,
            896519947090131496687170070074100632420837521538745909320),
    ])
    def test_small(self, _name, n, expected):
        """For small(ish) n, the correct number of BSTs is computed."""
        result = self.implementation(n)
        self.assertEqual(result, expected)

    @parameterized.expand([
        ('n900', 900, int(
            '14911141601602529426043429785823803628951022911660263050730316248'
            '47316847290968201766286968777066372263539597252879541571248521794'
            '78502608210002693084895624238517946854297406655412168859122531878'
            '65008268373402062319069664178074579029840324743181254535831553874'
            '79301538836396064991207804746864989491507532562163406155498238557'
            '14309001112941002489012843749283893149499782332851668608675218914'
            '02753042263304409353242220252198211792255416355532573240692103759'
            '60049144173135680776505398625736449947327041778444770066233724983'
            '517623825791401104')),
        ('n901', 901, int(
            '59545379211720965623734405863123437551531690163858389699257870429'
            '04695436742868583993531775537686333584556130049747348935296203442'
            '14596889991607206753651927391509583779577892209306687617028115107'
            '42527475256091162387238282006014006281025332289289222658608932435'
            '70337187238025084366220080596682585530388173269304422363752389448'
            '81309337038595887988275236346918606568179840313671519211139843157'
            '79064809570313173492659065796472238221401341144820763650746072884'
            '79043256443054015695091403381266843359503330915696299089328023714'
            '667939047118211504')),
        ('n902', 902, int(
            '23778586648667309195923174700157598650146542052145443328407960217'
            '84532862114594032544925313686478064109181550936809406451902337720'
            '08619754740834505819896882632755654386396221407171640702879665900'
            '04158812378013813019754290688115892209233371897583270975298317869'
            '67290797029935598474483899294754972693530426667675719495425372796'
            '50277017647970849621895958169101715978389424603665503684980096835'
            '76889003688875891873148238235003199449210768124941713590763049703'
            '49438536293870739822425204938299915520971097594905963955273184220'
            '9404859583508605408')),
        ('n903', 903, int(
            '94956524116912595350976394543770941512200239832129480548177805737'
            '19207557780624399875199538062152446276709512037480041251512653948'
            '57430657759305935851579365380805212759834468229966397054641143693'
            '75014726421050735620921448433737135924040345741455318828348371138'
            '84867010263349016031954509351842313521731017998129809046997340481'
            '60951364722538459220181868352275657834055113738089013609267864576'
            '46647459421285364670426039854382245588109372711326975733025010430'
            '98974685863797976503268794056706521051665555661073594998380746723'
            '0034892805825293720')),
    ])
    def test_large(self, _name, n, expected):
        """For larger n (about 900), the correct number of BSTs is computed."""
        result = self.implementation(n)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
