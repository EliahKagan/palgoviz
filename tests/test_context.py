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

"""Tests for context managers in context.py."""

import bisect
import contextlib
import enum
import inspect
import io
import sys
import types
import unittest
import weakref

from parameterized import param, parameterized, parameterized_class

from palgoviz import context, enumerations


class _FakeError(Exception):
    """Fake exception, for testing."""


class _NonRedirectingOutputCapturingTestCase(unittest.TestCase):
    """TestCase that captures output to a StringIO object, without patching."""

    def setUp(self):
        """Create a StringIO object to make assertions about."""
        super().setUp()
        self.__out = io.StringIO()

    @property
    def out(self):
        """A StringIO object we make assertions about."""
        return self.__out

    def assertOutputWas(self, expected):
        """Assert the output has expected content, and clear it."""
        actual = self.out.getvalue()
        self.out.seek(0)
        self.out.truncate(0)
        self.assertEqual(actual, expected)


class TestAnnounce(_NonRedirectingOutputCapturingTestCase):
    """Tests for the context.Announce context manager class."""

    def test_out_argument_not_accepted_positionally(self):
        expected_message = (r'\AAnnounce\.__init__\(\) takes 2 positional'
                            r' arguments but 3 were given\Z')
        with self.assertRaisesRegex(TypeError, expected_message):
            context.Announce('A', self.out)

    def test_repr_shows_name_and_out_if_not_none(self):
        expected = (r"Announce\('A', "
                    r'out=<_?io\.StringIO object at 0x[0-9a-fA-F]+>\)')
        cm = context.Announce('A', out=self.out)
        self.assertRegex(repr(cm), expected)

    def test_repr_shows_just_name_if_out_is_none(self):
        cm = context.Announce('A')
        self.assertEqual(repr(cm), "Announce('A')")

    def test_announces_single_completed_task(self):
        with context.Announce('A', out=self.out):
            with self.subTest(when='start'):
                self.assertOutputWas('Starting task A.\n')

        with self.subTest(when='finish'):
            self.assertOutputWas('Finished task A.\n')

    def test_announces_single_raising_task(self):
        with self.subTest('Exception should propagate.'):
            with self.assertRaises(_FakeError):
                with context.Announce('A', out=self.out):
                    with self.subTest(when='start'):
                        self.assertOutputWas('Starting task A.\n')
                    raise _FakeError

        with self.subTest(when='finish'):
            self.assertOutputWas('_FakeError raised in task A.\n')

    def test_announces_two_nested_completed_tasks(self):
        with context.Announce('A', out=self.out):
            with self.subTest(task='A', when='start'):
                self.assertOutputWas('Starting task A.\n')

            with context.Announce('B', out=self.out):
                with self.subTest(task='B', when='start'):
                    self.assertOutputWas('Starting task B.\n')

            with self.subTest(task='B', when='finish'):
                self.assertOutputWas('Finished task B.\n')

        with self.subTest(task='A', when='finish'):
            self.assertOutputWas('Finished task A.\n')

    def test_announces_two_nested_raising_tasks(self):
        with self.subTest('Exception should propagate.', scope='outer'):
            with self.assertRaises(_FakeError):
                with context.Announce('A', out=self.out):
                    with self.subTest(task='A', when='start'):
                        self.assertOutputWas('Starting task A.\n')

                    try:
                        with context.Announce('B', out=self.out):
                            with self.subTest(task='B', when='start'):
                                self.assertOutputWas('Starting task B.\n')
                            raise _FakeError
                    finally:
                        with self.subTest(task='B', when='finish'):
                            expected = '_FakeError raised in task B.\n'
                            self.assertOutputWas(expected)

        with self.subTest(task='A', when='finish'):
            self.assertOutputWas('_FakeError raised in task A.\n')

    @parameterized.expand([
        ('no error', False, 'Finished task A.\n'),
        ('with error', True, '_FakeError raised in task A.\n'),
    ])
    def test_if_out_is_none_stdout_is_used(self, _name, do_error, end_message):
        cm = context.Announce('A')
        old_stdout = sys.stdout
        out1 = io.StringIO()
        out2 = io.StringIO()
        sys.stdout = out1
        try:
            with cm:
                sys.stdout = out2
                if do_error:
                    raise _FakeError
        except _FakeError:
            pass
        finally:
            sys.stdout = old_stdout

        with self.subTest('__enter__'):
            self.assertEqual(out1.getvalue(), 'Starting task A.\n')
        with self.subTest('__exit__'):
            self.assertEqual(out2.getvalue(), end_message)

    def test_name_attribute_has_name(self):
        cm = context.Announce('A', out=self.out)
        self.assertEqual(cm.name, 'A')

    def test_name_attribute_is_read_only(self):
        cm = context.Announce('A', out=self.out)
        with self.assertRaises(AttributeError):
            cm.name = 'B'

    def test_new_attributes_cannot_be_created(self):
        cm = context.Announce('A', out=self.out)
        with self.assertRaises(AttributeError):
            cm.blah = 'B'


class _NoClose:
    """
    Class without a close method, to help test context.Closing.

    Derived classes may or may not have a close method.
    """

    def __repr__(self):
        """Representation of this object as Python code."""
        return f'{type(self).__name__}()'

    def __str__(self):
        """Non-code representation. Tests that reprs are used where needed."""
        return f'{type(self).__name__} instance'


class _HasClose(_NoClose):
    """Class with a close method, to help test context.Closing."""

    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


class TestContextlibClosing(unittest.TestCase):
    """
    Tests for contextlib.closing, reused below to test context.Closing.

    We needn't test contextlib.closing, but writing the tests so those that
    apply to both are used to test both has the effect of testing the tests.
    Also, in the future we will likely have another "closing" implementation.
    """

    @property
    def implementation(self):
        """The "closing" context manager implementation being tested."""
        return contextlib.closing

    def test_enter_returns_initializer_argument(self):
        obj = _HasClose()
        with self.implementation(obj) as ctx:
            self.assertIs(ctx, obj)

    def test_enter_does_not_close(self):
        obj = _HasClose()
        with self.implementation(obj):
            self.assertFalse(obj.closed)

    def test_exit_closes(self):
        obj = _HasClose()
        with self.implementation(obj):
            if obj.closed:
                raise Exception(
                    "can't check if __exit__ closes, already closed")
        self.assertTrue(obj.closed)

    def test_presence_of_close_is_not_pre_checked(self):
        got_to_exit = False
        try:
            with self.implementation(_NoClose()):
                got_to_exit = True
        except AttributeError:
            pass
        self.assertTrue(got_to_exit)

    def test_calling_close_attempted_even_if_absent(self):
        with self.subTest('AttributeError raised'):
            with self.assertRaises(AttributeError) as ctx:
                with self.implementation(_NoClose()):
                    pass

        with self.subTest('AttributeError name attribute'):
            self.assertEqual(ctx.exception.name, 'close')

    def test_exit_closes_even_if_close_was_just_patched_in(self):
        closed = False

        def just_in_time_close():
            nonlocal closed
            closed = True

        obj = _NoClose()
        with self.implementation(obj):
            obj.close = just_in_time_close

        self.assertTrue(closed)


class TestClosing(TestContextlibClosing):
    """Tests for the context.Closing class."""

    @property
    def implementation(self):
        return context.Closing

    def test_repr_shows_type_and_initializer_argument(self):
        cm = self.implementation(_HasClose())
        self.assertEqual(repr(cm), 'Closing(_HasClose())')


class TestContextlibSuppress(unittest.TestCase):
    """
    Tests for contextlib.suppress, reused below to test context.Suppress.

    We needn't test contextlib.suppress, but writing the tests so those that
    apply to both are used to test both has the effect of testing the tests.
    Also, in the future we will likely have another "suppress" implementation.
    """

    @property
    def implementation(self):
        """The "suppress" context manager implementation being tested."""
        return contextlib.suppress

    def test_enter_returns_none(self):
        """The __enter__ method should implicitly return None."""
        with self.implementation(ValueError) as ctx:
            pass
        self.assertIsNone(ctx)

    @parameterized.expand([
        ([ValueError], ValueError),
        ([ValueError, TypeError], ValueError),
        ([ValueError, TypeError], TypeError),
    ])
    def test_listed_exception_suppressed(self, to_suppress, to_raise):
        try:
            with self.implementation(*to_suppress):
                raise to_raise()
        except to_raise:
            self.fail(f'{to_raise.__name__} exception was not suppressed')

    @parameterized.expand([
        ([], ValueError),
        ([ValueError], TypeError),
        ([ValueError, TypeError], AttributeError),
    ])
    def test_unlisted_exception_not_suppressed(self, to_suppress, to_raise):
        with self.assertRaises(to_raise):
            with self.implementation(*to_suppress):
                raise to_raise()

    @parameterized.expand([
        ([LookupError], KeyError),
        ([LookupError], IndexError),
        ([SystemExit, Exception], ValueError),
    ])
    def test_indirect_listed_exception_suppressed(self, to_suppress, to_raise):
        """Indirect instances (instances of subclasses) are suppressed."""
        try:
            with self.implementation(*to_suppress):
                raise to_raise()
        except to_raise:
            self.fail(f'{to_raise.__name__} exception was not suppressed')

    def test_with_no_exception_nothing_is_raised(self):
        """Fail on likely bug in __exit__; let other exceptions error out."""
        try:
            with self.implementation(ValueError):
                pass
        except TypeError as error:
            self.fail(f'TypeError when with suite should succeed: {error}')


class TestSuppress(TestContextlibSuppress):
    """Tests for the context.Suppress context manager class."""

    @property
    def implementation(self):
        return context.Suppress

    @parameterized.expand([
        ([], 'Suppress()'),
        ([ValueError], 'Suppress(ValueError)'),
        ([ValueError, TypeError, AttributeError],
            'Suppress(ValueError, TypeError, AttributeError)')
    ])
    def test_repr_shows_exception_type_names(self, to_suppress, expected):
        cm = context.Suppress(*to_suppress)
        self.assertEqual(repr(cm), expected)


@enum.unique
class _Access(enumerations.CodeReprEnum):
    """Kind of access that occurred, for _AttributeSpy history entries."""

    GET_ATTEMPT = enum.auto()
    """An attempt was made to read the attribute, raising AttributeError."""

    GET = enum.auto()
    """The attribute was read with no error."""

    SET_ATTEMPT = enum.auto()
    """An attempt was made to set the attribute, raising AttributeError."""

    SET = enum.auto()
    """The attribute was set with no error."""

    DELETE_ATTEMPT = enum.auto()
    """An attempt was made to delete te attribute, raising AttributeError."""

    DELETE = enum.auto()
    """The attribute was deleted with no error."""


_attribute_spy_histories = weakref.WeakKeyDictionary()


def _log_access(spy, access, *args):
    """Log an access in _attribute_spy_histories. Helper for _AttributeSpy."""
    _attribute_spy_histories[spy].append((access, *args))


class _AttributeSpy:
    r"""
    Class that records successful accesses to its attributes.

    >>> spy = _AttributeSpy(x=10, y=20)
    >>> spy
    _AttributeSpy(x=10, y=20)
    >>> spy.w = 30
    >>> spy.x += 5
    >>> spy.history
    [(_Access.SET, 'w', 30), (_Access.GET, 'x', 10), (_Access.SET, 'x', 15)]
    >>> spy.history.clear()
    >>> del spy.w
    >>> spy.__dict__
    {'x': 15, 'y': 20}
    >>> spy.history
    [(_Access.DELETE, 'w'), (_Access.GET, '__dict__', {'x': 15, 'y': 20})]
    >>> import re; [s for s in dir(spy) if not re.match(r'\A__\w+__\Z', s)]
    ['history', 'x', 'y']
    """

    def __init__(self, **initial):
        """Create a new _AttributeSpy with the given initial attributes."""
        for name, value in initial.items():
            super().__setattr__(name, value)

        _attribute_spy_histories[self] = []

    def __repr__(self):
        """Representation as Python code."""
        items = super().__getattribute__('__dict__').items()
        joined = ', '.join(f'{name}={value!r}' for name, value in items)
        return f'{type(self).__name__}({joined})'

    def __dir__(self):
        """List all attributes, including the dynamic 'history' attribute."""
        names = super().__dir__()
        bisect.insort(names, 'history')
        return names

    def __getattribute__(self, name):
        """Get the named attribute, logging to history if successful."""
        if name == 'history':
            return _attribute_spy_histories[self]

        getter = super().__getattribute__
        try:
            value = getter(name)
        except AttributeError:
            _log_access(self, _Access.GET_ATTEMPT, name)
            raise
        _log_access(self, _Access.GET, name, value)
        return value

    def __setattr__(self, name, value):
        """Set the named attribute, logging to history if successful."""
        if name == 'history':
            raise RuntimeError("attempt to set 'history' indicates a bug")

        setter = super().__setattr__
        try:
            setter(name, value)
        except AttributeError:
            _log_access(self, _Access.SET_ATTEMPT, name, value)
            raise
        _log_access(self, _Access.SET, name, value)

    def __delattr__(self, name):
        """Delete the named attribute, logging to history if successful."""
        if name == 'history':
            raise RuntimeError("attempt to delete 'history' indicates a bug")

        deleter = super().__delattr__
        try:
            deleter(name)
        except AttributeError:
            _log_access(self, _Access.DELETE_ATTEMPT, name)
            raise
        _log_access(self, _Access.DELETE, name)


@parameterized_class(('implementation_name', 'implementation'), [
    (context.MonkeyPatch.__name__, context.MonkeyPatch),
    (context.MonkeyPatchAlt.__name__, context.MonkeyPatchAlt),
])
class TestMonkeyPatch(unittest.TestCase):
    """Test for context.TestMonkeyPatch and self.TestMonkeyPatchAlt."""

    _DENY_ABSENT_KWARGS = [
        param('if allow_absent unspecified'),
        param('if allow_absent false', allow_absent=False),
    ]

    _DENY_ABSENT_AND_ALLOW_ABSENT_KWARGS = [
        *_DENY_ABSENT_KWARGS,
        param('if allow_absent true', allow_absent=True),
    ]

    @parameterized.expand(_DENY_ABSENT_KWARGS)
    def test_repr_looks_like_code(self, _name, **kwargs):
        expected = (self.implementation_name
                    + "(namespace(a=10), 'a', 20, allow_absent=False)")
        target = types.SimpleNamespace(a=10)
        patcher = self.implementation(target, 'a', 20, **kwargs)
        self.assertEqual(repr(patcher), expected)

    def test_repr_looks_like_code_if_allow_absent_true(self):
        expected = (self.implementation_name
                    + "(namespace(a=10), 'a', 20, allow_absent=True)")
        target = types.SimpleNamespace(a=10)
        patcher = self.implementation(target, 'a', 20, allow_absent=True)
        self.assertEqual(repr(patcher), expected)

    def test_allow_absent_not_accepted_positionally(self):
        expected_message = (fr'\A{self.implementation_name}\.__init__\(\) '
                            r'takes 4 positional arguments but 5 were given\Z')

        with self.assertRaisesRegex(TypeError, expected_message):
            self.implementation(10, 'a', 4, True)

    def test_new_attributes_cannot_be_created(self):
        # Change the example if a target attribute is added in the future.
        expected_message = (fr"\A'{self.implementation_name}' object has no "
                            r"attribute 'target'\Z")

        target = types.SimpleNamespace(a=10)
        patcher = self.implementation(target, 'a', 20)

        with self.assertRaisesRegex(AttributeError, expected_message):
            patcher.target = types.SimpleNamespace(c=15, d=17)

    @parameterized.expand(_DENY_ABSENT_AND_ALLOW_ABSENT_KWARGS)
    def test_construction_does_not_patch(self, _name, **kwargs):
        target = types.SimpleNamespace(a=10)
        _ = self.implementation(target, 'a', 20, **kwargs)  # Hold the ref.
        self.assertEqual(target.a, 10)

    @parameterized.expand(_DENY_ABSENT_AND_ALLOW_ABSENT_KWARGS)
    def test_construction_does_not_check_writeable(self, _name, **kwargs):
        """Construction shouldn't fail fast, since the situation may change."""
        target = 3.0
        try:
            self.implementation(target, 'numerator', 4.0, **kwargs)
        except AttributeError:
            self.fail("shouldn't check writability on construction")

    @parameterized.expand(_DENY_ABSENT_KWARGS)
    def test_construction_does_not_check_existence(self, _name, **kwargs):
        """Construction shouldn't fail fast, since the situation may change."""
        target = types.SimpleNamespace(a=10)
        try:
            self.implementation(target, 'b', 15, **kwargs)
        except AttributeError:
            self.fail("shouldn't check existence on construction")

    def test_enter_returns_none(self):
        """The __enter__ method should implicitly return None."""
        target = types.SimpleNamespace(a=10)
        with self.implementation(target, 'a', 20) as ctx:
            pass
        self.assertIsNone(ctx)

    @parameterized.expand(_DENY_ABSENT_AND_ALLOW_ABSENT_KWARGS)
    def test_cm_patches_existing(self, _name, **kwargs):
        target = types.SimpleNamespace(a=10)
        with self.implementation(target, 'a', 20, **kwargs):
            self.assertEqual(target.a, 20)

    @parameterized.expand(_DENY_ABSENT_AND_ALLOW_ABSENT_KWARGS)
    def test_cm_patches_existing_not_via_dict(self, _name, **kwargs):
        """Patched attribute needn't be settable via instance dictionary."""
        class Target:  # Target.__dict__ is a mappingproxy (not writeable).
            a = 10

        with self.implementation(Target, 'a', 20, **kwargs):
            self.assertEqual(Target.a, 20)

    @parameterized.expand(_DENY_ABSENT_AND_ALLOW_ABSENT_KWARGS)
    def test_cm_enters_with_existing(self, _name, **kwargs):
        target = types.SimpleNamespace(a=10)
        entered = False
        with self.implementation(target, 'a', 20, **kwargs):
            entered = True
        self.assertTrue(entered)

    @parameterized.expand(_DENY_ABSENT_AND_ALLOW_ABSENT_KWARGS)
    def test_cm_unpatches_existing(self, _name, **kwargs):
        target = types.SimpleNamespace(a=10)
        with self.implementation(target, 'a', 20, **kwargs):
            pass
        self.assertEqual(target.a, 10)

    @parameterized.expand(_DENY_ABSENT_AND_ALLOW_ABSENT_KWARGS)
    def test_cm_unpatches_existing_not_via_dict(self, _name, **kwargs):
        """Patched attribute needn't be deletable via instance dictionary."""
        class Target:  # Target.__dict__ is a mappingproxy (not writeable).
            a = 10

        with self.implementation(Target, 'a', 20, **kwargs):
            pass

        self.assertEqual(Target.a, 10)

    @parameterized.expand(_DENY_ABSENT_AND_ALLOW_ABSENT_KWARGS)
    def test_cm_unpatches_existing_on_error(self, _name, **kwargs):
        target = types.SimpleNamespace(a=10)

        with contextlib.suppress(_FakeError):
            with self.implementation(target, 'a', 20, **kwargs):
                raise _FakeError

        self.assertEqual(target.a, 10)

    @parameterized.expand(_DENY_ABSENT_KWARGS)
    def test_cm_refuses_to_patch_nonexisting(self, _name, **kwargs):
        expected_message = (
            r"\A'types\.SimpleNamespace' object has no attribute 'b'\Z")

        target = types.SimpleNamespace(a=10)

        with self.assertRaisesRegex(AttributeError, expected_message):
            with self.implementation(target, 'b', 15, **kwargs):
                pass

    @parameterized.expand(_DENY_ABSENT_KWARGS)
    def test_cm_does_not_enter_with_nonexisting(self, _name, **kwargs):
        target = types.SimpleNamespace(a=10)
        entered = False

        with contextlib.suppress(AttributeError):
            with self.implementation(target, 'b', 15, **kwargs):
                entered = True

        self.assertFalse(entered)

    @parameterized.expand(_DENY_ABSENT_KWARGS)
    def test_cm_does_not_add_nonexisting(self, _name, **kwargs):
        target = types.SimpleNamespace(a=10)

        with contextlib.suppress(AttributeError):
            with self.implementation(target, 'b', 15, **kwargs):
                pass

        with self.assertRaises(AttributeError):
            target.b

    def test_cm_patches_nonexisting_if_allow_absent_true(self):
        target = types.SimpleNamespace(a=10)
        with self.implementation(target, 'b', 15, allow_absent=True):
            self.assertEqual(target.b, 15)

    def test_cm_patches_nonexisting_not_via_dict_if_allow_absent_true(self):
        """Patched attribute needn't be settable via instance dictionary."""
        class Target:  # Target.__dict__ is a mappingproxy (not writeable).
            a = 10

        with self.implementation(Target, 'b', 15, allow_absent=True):
            self.assertEqual(Target.b, 15)

    def test_cm_enters_with_nonexisting_if_allow_absent_true(self):
        target = types.SimpleNamespace(a=10)
        entered = False
        with self.implementation(target, 'b', 15, allow_absent=True):
            entered = True
        self.assertTrue(entered)

    def test_cm_unpatches_nonexisting_if_allow_absent_true(self):
        target = types.SimpleNamespace(a=10)
        with self.implementation(target, 'b', 15, allow_absent=True):
            pass
        with self.assertRaises(AttributeError):
            target.b

    def test_cm_unpatches_nonexisting_not_via_dict_if_allow_absent_true(self):
        """Patched attribute needn't be deletable via instance dictionary."""
        class Target:  # Target.__dict__ is a mappingproxy (not writeable).
            a = 10

        with self.implementation(Target, 'b', 15, allow_absent=True):
            pass
        with self.assertRaises(AttributeError):
            Target.b

    def test_cm_unpatches_nonexisting_on_error_if_allow_absent_true(self):
        target = types.SimpleNamespace(a=10)

        with contextlib.suppress(_FakeError):
            with self.implementation(target, 'b', 15, allow_absent=True):
                raise _FakeError

        with self.assertRaises(AttributeError):
            target.b

    @parameterized.expand(_DENY_ABSENT_KWARGS)
    def test_cm_patches_just_created(self, _name, **kwargs):
        """It doesn't matter what existed when the patcher was constructed."""
        target = types.SimpleNamespace(a=10)
        patcher = self.implementation(target, 'c', 30, **kwargs)
        target.c = 25
        with patcher:
            self.assertEqual(target.c, 30)

    @parameterized.expand(_DENY_ABSENT_KWARGS)
    def test_cm_refuses_to_patch_just_deleted(self, _name, **kwargs):
        """It doesn't matter what existed when the patcher was constructed."""
        expected_message = (
            r"\A'types\.SimpleNamespace' object has no attribute 'c'\Z")

        target = types.SimpleNamespace(a=10, c=25)
        patcher = self.implementation(target, 'c', 30, **kwargs)
        del target.c

        with self.assertRaisesRegex(AttributeError, expected_message):
            with patcher:
                pass

    def test_cm_unpatches_just_deleted_if_allow_absent_true(self):
        """It doesn't matter what existed when the patcher was constructed."""
        target = types.SimpleNamespace(a=10, c=25)
        patcher = self.implementation(target, 'c', 30, allow_absent=True)
        del target.c

        with patcher:
            # Usually I don't check this, since at least one test should fail
            # whenever there is a bug. Here the situation is conceptually
            # complicated enough, I think this may help make the tests clearer.
            try:
                target.c
            except AttributeError as error:
                raise Exception("not patched, can't test unpatch") from error

        with self.assertRaises(AttributeError):
            target.c

    @parameterized.expand(_DENY_ABSENT_AND_ALLOW_ABSENT_KWARGS)
    def test_decoration_itself_does_not_patch(self, _name, **kwargs):
        """Patching and unpatching happens per call, not in the definition."""
        target = types.SimpleNamespace(a=10)

        @self.implementation(target, 'a', 20, **kwargs)
        def _decorated_function():
            pass

        self.assertEqual(target.a, 10)

    @parameterized.expand(_DENY_ABSENT_AND_ALLOW_ABSENT_KWARGS)
    def test_decoration_itself_does_not_check_writeable(self, _name, **kwargs):
        """Decoration shouldn't fail fast, since the situation may change."""
        target = 3.0
        try:
            @self.implementation(target, 'numerator', 4.0, **kwargs)
            def _decorated_function():
                pass
        except AttributeError:
            self.fail("shouldn't check writability before function is called")

    @parameterized.expand(_DENY_ABSENT_KWARGS)
    def test_decoration_itself_does_not_check_existence(self, _name, **kwargs):
        """Decoration shouldn't fail fast, since the situation may change."""
        target = types.SimpleNamespace(a=10)
        try:
            @self.implementation(target, 'b', 15, **kwargs)
            def _decorated_function():
                pass
        except AttributeError:
            self.fail("shouldn't check existence before function is called")

    @parameterized.expand(_DENY_ABSENT_AND_ALLOW_ABSENT_KWARGS)
    def test_wrapper_patches_existing(self, _name, **kwargs):
        target = types.SimpleNamespace(a=10)

        @self.implementation(target, 'a', 20, **kwargs)
        def decorated_function():
            self.assertEqual(target.a, 20)

        decorated_function()

    @parameterized.expand(_DENY_ABSENT_AND_ALLOW_ABSENT_KWARGS)
    def test_wrapper_patches_existing_not_via_dict(self, _name, **kwargs):
        """Patched attribute needn't be settable via instance dictionary."""
        class Target:  # Target.__dict__ is a mappingproxy (not writeable).
            a = 10

        @self.implementation(Target, 'a', 20, **kwargs)
        def decorated_function():
            self.assertEqual(Target.a, 20)

        decorated_function()

    @parameterized.expand(_DENY_ABSENT_AND_ALLOW_ABSENT_KWARGS)
    def test_wrapper_calls_wrapped(self, _name, **kwargs):
        target = types.SimpleNamespace(a=10)
        called = False

        @self.implementation(target, 'a', 20, **kwargs)
        def decorated_function():
            nonlocal called
            called = True

        decorated_function()
        self.assertTrue(called)

    @parameterized.expand(_DENY_ABSENT_AND_ALLOW_ABSENT_KWARGS)
    def test_wrapper_unpatches_existing(self, _name, **kwargs):
        target = types.SimpleNamespace(a=10)

        @self.implementation(target, 'a', 20, **kwargs)
        def decorated_function():
            pass

        decorated_function()
        self.assertEqual(target.a, 10)

    @parameterized.expand(_DENY_ABSENT_AND_ALLOW_ABSENT_KWARGS)
    def test_wrapper_unpatches_existing_not_via_dict(self, _name, **kwargs):
        """Patched attribute needn't be deletable via instance dictionary."""
        class Target:  # Target.__dict__ is a mappingproxy (not writeable).
            a = 10

        @self.implementation(Target, 'a', 20, **kwargs)
        def decorated_function():
            pass

        decorated_function()
        self.assertEqual(Target.a, 10)

    @parameterized.expand(_DENY_ABSENT_AND_ALLOW_ABSENT_KWARGS)
    def test_wrapper_unpatches_existing_on_error(self, _name, **kwargs):
        target = types.SimpleNamespace(a=10)

        @self.implementation(target, 'a', 20, **kwargs)
        def decorated_function():
            raise _FakeError

        with contextlib.suppress(_FakeError):
            decorated_function()

        self.assertEqual(target.a, 10)

    @parameterized.expand(_DENY_ABSENT_KWARGS)
    def test_wrapper_refuses_to_patch_nonexisting(self, _name, **kwargs):
        expected_message = (
            r"\A'types\.SimpleNamespace' object has no attribute 'b'\Z")

        target = types.SimpleNamespace(a=10)

        @self.implementation(target, 'b', 15, **kwargs)
        def decorated_function():
            pass

        with self.assertRaisesRegex(AttributeError, expected_message):
            decorated_function()

    @parameterized.expand(_DENY_ABSENT_KWARGS)
    def test_wrapper_does_not_call_wrapped_with_nonexisting(self, _name,
                                                            **kwargs):
        target = types.SimpleNamespace(a=10)
        called = False

        @self.implementation(target, 'b', 15, **kwargs)
        def decorated_function():
            nonlocal called
            called = True

        with contextlib.suppress(AttributeError):
            decorated_function()

        self.assertFalse(called)

    @parameterized.expand(_DENY_ABSENT_KWARGS)
    def test_wrapper_does_not_add_nonexisting(self, _name, **kwargs):
        target = types.SimpleNamespace(a=10)

        @self.implementation(target, 'b', 15, **kwargs)
        def decorated_function():
            pass

        with contextlib.suppress(AttributeError):
            decorated_function()

        with self.assertRaises(AttributeError):
            target.b

    def test_wrapper_patches_nonexisting_if_allow_absent_true(self):
        target = types.SimpleNamespace(a=10)

        @self.implementation(target, 'b', 15, allow_absent=True)
        def decorated_function():
            self.assertEqual(target.b, 15)

        decorated_function()

    def test_wrapper_patches_nonexisting_not_via_dict_if_allow_absent_true(
            self):
        """Patched attribute needn't be settable via instance dictionary."""
        class Target:  # Target.__dict__ is a mappingproxy (not writeable).
            a = 10

        @self.implementation(Target, 'b', 15, allow_absent=True)
        def decorated_function():
            self.assertEqual(Target.b, 15)

        decorated_function()

    def test_wrapper_calls_wrapped_with_nonexisting_if_allow_absent_true(self):
        target = types.SimpleNamespace(a=10)
        called = False

        @self.implementation(target, 'b', 15, allow_absent=True)
        def decorated_function():
            nonlocal called
            called = True

        decorated_function()
        self.assertTrue(called)

    def test_wrapper_unpatches_nonexisting_if_allow_absent_true(self):
        target = types.SimpleNamespace(a=10)

        @self.implementation(target, 'b', 15, allow_absent=True)
        def decorated_function():
            pass

        decorated_function()
        with self.assertRaises(AttributeError):
            target.b

    def test_wrapper_unpatches_nonexisting_not_via_dict_if_allow_absent_true(
            self):
        """Patched attribute needn't be deletable via instance dictionary."""
        class Target:  # Target.__dict__ is a mappingproxy (not writeable).
            a = 10

        @self.implementation(Target, 'b', 15, allow_absent=True)
        def decorated_function():
            pass

        decorated_function()
        with self.assertRaises(AttributeError):
            Target.b

    def test_wrapper_unpatches_nonexisting_on_error_if_allow_absent_true(self):
        target = types.SimpleNamespace()

        @self.implementation(target, 'b', 15, allow_absent=True)
        def decorated_function():
            raise _FakeError

        with contextlib.suppress(_FakeError):
            decorated_function()

        with self.assertRaises(AttributeError):
            target.b

    @parameterized.expand(_DENY_ABSENT_KWARGS)
    def test_wrapper_patches_just_created(self, _name, **kwargs):
        """It doesn't matter what existed when the decorated def was run."""
        target = types.SimpleNamespace(a=10)

        @self.implementation(target, 'c', 30, **kwargs)
        def decorated_function():
            self.assertEqual(target.c, 30)

        target.c = 25
        decorated_function()

    @parameterized.expand(_DENY_ABSENT_KWARGS)
    def test_wrapper_refuses_to_patch_just_deleted(self, _name, **kwargs):
        """It doesn't matter what existed when the decorated def was run."""
        expected_message = (
            r"\A'types\.SimpleNamespace' object has no attribute 'c'\Z")

        target = types.SimpleNamespace(a=10, c=25)

        @self.implementation(target, 'c', 30, **kwargs)
        def decorated_function():
            pass

        del target.c

        with self.assertRaisesRegex(AttributeError, expected_message):
            decorated_function()

    def test_wrapper_unpatches_just_deleted_if_allow_absent_true(self):
        """It doesn't matter what existed when the decorated def was run."""
        target = types.SimpleNamespace(a=10, c=25)

        @self.implementation(target, 'c', 30, allow_absent=True)
        def decorated_function():
            # Usually I don't check this, since at least one test should fail
            # whenever there is a bug. Here the situation is conceptually
            # complicated enough, I think this may help make the tests clearer.
            try:
                target.c
            except AttributeError as error:
                raise Exception("not patched, can't test unpatch") from error

        del target.c
        decorated_function()
        with self.assertRaises(AttributeError):
            target.c

    def test_wrapper_forwards_arbitrary_args_and_return(self):
        target = types.SimpleNamespace(a=10)

        @self.implementation(target, 'a', 20)
        def decorated_function(x, y, p, q, r, *, u, v, w, **kwargs):
            return (x, y, p, q, r, u, v, w, kwargs)

        expected = (1, 2, 3, 4, 5, 8, 7, 9, {'m': 10, 'n': 11})
        actual = decorated_function(1, 2, r=5, p=3, q=4, v=7, u=8, w=9,
                                    m=10, n=11)
        self.assertTupleEqual(actual, expected)

    def test_wrapper_has_wrapped_metadata(self):
        serious_numbers = types.SimpleNamespace()

        class C:
            @staticmethod
            @self.implementation(serious_numbers, 'two', 2, allow_absent=True)
            def halve(x: int) -> float:
                """Find half x."""
                return x / serious_numbers.two

        with self.subTest('__module__'):
            if __name__ not in ('tests.test_context', '__main__'):
                raise Exception(
                    f"can't reliably test __module__: {__name__=}, expected "
                    "'tests.test_context' or '__main__'")
            self.assertEqual(C.halve.__module__, __name__)
        with self.subTest('__name__'):
            self.assertEqual(C.halve.__name__, 'halve')
        with self.subTest('__qualname__'):
            expected_qualname = (
                'TestMonkeyPatch.test_wrapper_has_wrapped_metadata.<locals>'
                '.C.halve')
            self.assertEqual(C.halve.__qualname__, expected_qualname)
        with self.subTest('__doc__'):
            # Formats the docstring. In this case, we could just check __doc__.
            self.assertEqual(inspect.getdoc(C.halve), "Find half x.")
        with self.subTest('__annotations__'):
            # Better than checking __annotations__, even here, due to PEP 563.
            self.assertDictEqual(inspect.get_annotations(C.halve),
                                 {'x': int, 'return': float})

    def test_wrapper_exposes_wrapped(self):
        """The wrapper has a __wrapped__ attribute (see the functools docs)."""
        target = types.SimpleNamespace(a=10)

        @self.implementation(target, 'a', 20)
        def decorated_function():
            return target.a

        if decorated_function() != 20:
            raise Exception("not patched, can't contrast to unpatched version")

        original = decorated_function.__wrapped__
        self.assertEqual(original(), 10)

    def test_separate_wrappers_can_nest_calls(self):
        target = types.SimpleNamespace()

        @self.implementation(target, 'x', 50, allow_absent=True)
        def direct():
            return indirect() + target.x

        @self.implementation(target, 'x', 12)
        def indirect():
            return target.x

        self.assertEqual(direct(), 62)

    def test_separate_wrappers_can_nest_calls_with_errors(self):
        target = types.SimpleNamespace()

        @self.implementation(target, 'x', 50, allow_absent=True)
        def direct():
            try:
                indirect()
            except _FakeError as error:
                return error.value + target.x

        @self.implementation(target, 'x', 12)
        def indirect():
            error = _FakeError()
            error.value = target.x
            raise error

        self.assertEqual(direct(), 62)

    def test_wrappers_from_same_decorator_can_nest_calls(self):
        target = _AttributeSpy(a=10)
        patcher = self.implementation(target, 'a', 20)

        @patcher
        def direct():
            indirect()

        @patcher
        def indirect():
            del target.a

        direct()

        self.assertListEqual(target.history, [
            (_Access.GET, 'a', 10),
            (_Access.SET, 'a', 20),
            (_Access.GET, 'a', 20),
            (_Access.SET, 'a', 20),
            (_Access.DELETE, 'a'),  # Done inside indirect, not by a wrapper.
            (_Access.SET, 'a', 20),
            (_Access.SET, 'a', 10),
        ])

    def test_wrappers_from_the_same_decorator_can_nest_calls_with_errors(self):
        target = _AttributeSpy(a=10)
        patcher = self.implementation(target, 'a', 20)

        @patcher
        def direct():
            indirect()

        @patcher
        def indirect():
            del target.a
            raise _FakeError

        with contextlib.suppress(_FakeError):
            direct()

        self.assertListEqual(target.history, [
            (_Access.GET, 'a', 10),
            (_Access.SET, 'a', 20),
            (_Access.GET, 'a', 20),
            (_Access.SET, 'a', 20),
            (_Access.DELETE, 'a'),  # Done inside indirect, not by a wrapper.
            (_Access.SET, 'a', 20),
            (_Access.SET, 'a', 10),
        ])

    def test_decorated_defs_can_nest_with_nested_calls(self):
        target = _AttributeSpy(x=0)
        patcher1 = self.implementation(target, 'x', 1)
        patcher2 = self.implementation(target, 'x', 2)

        @patcher1
        def f(repeat):
            @patcher2
            def g():
                @patcher1
                def ff():
                    @patcher2
                    def gg():
                        if repeat:
                            f(False)
                        else:
                            del target.x

                    gg()

                ff()

            g()

        f(True)

        self.assertListEqual(target.history, [
            (_Access.GET, 'x', 0),  # f (note: 0, not 2)
            (_Access.SET, 'x', 1),  # f
            (_Access.GET, 'x', 1),  # g
            (_Access.SET, 'x', 2),  # g
            (_Access.GET, 'x', 2),  # ff
            (_Access.SET, 'x', 1),  # ff
            (_Access.GET, 'x', 1),  # gg
            (_Access.SET, 'x', 2),  # gg
            (_Access.GET, 'x', 2),  # f (note: 2, not 0)
            (_Access.SET, 'x', 1),  # f
            (_Access.GET, 'x', 1),  # g
            (_Access.SET, 'x', 2),  # g
            (_Access.GET, 'x', 2),  # ff
            (_Access.SET, 'x', 1),  # ff
            (_Access.GET, 'x', 1),  # gg
            (_Access.SET, 'x', 2),  # gg
            (_Access.DELETE, 'x'),  # gg (wrapped)
            (_Access.SET, 'x', 1),  # gg
            (_Access.SET, 'x', 2),  # ff
            (_Access.SET, 'x', 1),  # g
            (_Access.SET, 'x', 2),  # f (note: 2, not 0)
            (_Access.SET, 'x', 1),  # gg
            (_Access.SET, 'x', 2),  # ff
            (_Access.SET, 'x', 1),  # g
            (_Access.SET, 'x', 0),  # f (note: 0, not 2)
        ])

    def test_decorated_defs_can_nest_with_nested_calls_with_errors(self):
        target = _AttributeSpy(x=0)
        patcher1 = self.implementation(target, 'x', 1)
        patcher2 = self.implementation(target, 'x', 2)

        @patcher1
        def f(repeat):
            @patcher2
            def g():
                @patcher1
                def ff():
                    @patcher2
                    def gg():
                        if repeat:
                            f(False)
                        else:
                            del target.x
                            raise _FakeError

                    gg()

                ff()

            g()

        with contextlib.suppress(_FakeError):
            f(True)

        self.assertListEqual(target.history, [
            (_Access.GET, 'x', 0),  # f (note: 0, not 2)
            (_Access.SET, 'x', 1),  # f
            (_Access.GET, 'x', 1),  # g
            (_Access.SET, 'x', 2),  # g
            (_Access.GET, 'x', 2),  # ff
            (_Access.SET, 'x', 1),  # ff
            (_Access.GET, 'x', 1),  # gg
            (_Access.SET, 'x', 2),  # gg
            (_Access.GET, 'x', 2),  # f (note: 2, not 0)
            (_Access.SET, 'x', 1),  # f
            (_Access.GET, 'x', 1),  # g
            (_Access.SET, 'x', 2),  # g
            (_Access.GET, 'x', 2),  # ff
            (_Access.SET, 'x', 1),  # ff
            (_Access.GET, 'x', 1),  # gg
            (_Access.SET, 'x', 2),  # gg
            (_Access.DELETE, 'x'),  # gg (wrapped)
            (_Access.SET, 'x', 1),  # gg
            (_Access.SET, 'x', 2),  # ff
            (_Access.SET, 'x', 1),  # g
            (_Access.SET, 'x', 2),  # f (note: 2, not 0)
            (_Access.SET, 'x', 1),  # gg
            (_Access.SET, 'x', 2),  # ff
            (_Access.SET, 'x', 1),  # g
            (_Access.SET, 'x', 0),  # f (note: 0, not 2)
        ])

    def test_decorated_defs_can_nest_with_nested_calls_allowing_absent(self):
        target = _AttributeSpy()
        patcher1 = self.implementation(target, 'x', 1, allow_absent=True)
        patcher2 = self.implementation(target, 'x', 2, allow_absent=True)

        @patcher1
        def f(repeat):
            @patcher2
            def g():
                @patcher1
                def ff():
                    @patcher2
                    def gg():
                        if repeat:
                            f(False)

                    gg()

                del target.x
                ff()

            g()

        f(True)

        self.assertListEqual(target.history, [
            (_Access.GET_ATTEMPT, 'x'),  # f
            (_Access.SET, 'x', 1),  # f
            (_Access.GET, 'x', 1),  # g
            (_Access.SET, 'x', 2),  # g
            (_Access.DELETE, 'x'),  # g (wrapped)
            (_Access.GET_ATTEMPT, 'x'),  # ff
            (_Access.SET, 'x', 1),  # ff
            (_Access.GET, 'x', 1),  # gg
            (_Access.SET, 'x', 2),  # gg
            (_Access.GET, 'x', 2),  # f
            (_Access.SET, 'x', 1),  # f
            (_Access.GET, 'x', 1),  # g
            (_Access.SET, 'x', 2),  # g
            (_Access.DELETE, 'x'),  # g (wrapped)
            (_Access.GET_ATTEMPT, 'x'),  # ff
            (_Access.SET, 'x', 1),  # ff
            (_Access.GET, 'x', 1),  # gg
            (_Access.SET, 'x', 2),  # gg
            (_Access.SET, 'x', 1),  # gg
            (_Access.DELETE, 'x'),  # ff
            (_Access.SET, 'x', 1),  # g
            (_Access.SET, 'x', 2),  # f
            (_Access.SET, 'x', 1),  # gg
            (_Access.DELETE, 'x'),  # ff
            (_Access.SET, 'x', 1),  # g
            (_Access.DELETE, 'x'),  # f
        ])


if __name__ == '__main__':
    unittest.main()
