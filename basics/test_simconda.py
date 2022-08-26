"""Tests for the classes in simconda.py."""

# FIXME: Write unittest tests for simconda.Simulator, a class whose instances
# simulate the effect of conda's activate and deactivate commands on what Conda
# environment, if any, is active. This is more subtle than it may first appear.
# You'll need to do some experiments. Make several throwaway Conda environments
# (e.g., "conda create -yn alfa", "conda create -yn bravo", and so on). Figure
# out the rules that determine what environment is active at any point in any
# series of "conda activate", "conda activate <name>", and "conda deactivate"
# commands. Each time you discover something about how this works, write a unit
# test in this module that expresses that behavior in terms of the simulator
# you will build (and that will test that the simulator behaves correctly). In
# this way, once you have figured out how the simulator should work, you will
# have already completed the tests and can write the simulator.
#
# If you can, do all the experimentation in a Docker container. If not, make
# sure to name the new environments so you don't confuse them with anything
# important. It is possible to interleave activation and deactivation with
# environment creation and deletion, but don't support this: instead, take an
# iterable of environment names on construction, representing environments
# other than the base environment that already exist prior to the simulation,
# and do not otherwise support creation and deletion. It would be strange for a
# user to give any duplicate names (that is, to list any name twice, or to list
# "base" at all). Decide what to do if this happens, and write tests for it.
# Each instance of the simulator represents a running shell configured for use
# with Conda, so it starts with the base environment active. It's up to you how
# one issues commands and how one queries for which environment is active, but
# you need not parse or otherwise support actual shell commands, which I would
# recommend against doing: if the simulator offers a good object-oriented
# interface, a command-line interface could easily be built atop it if needed.
#
# The simulator need only perform well for realistic uses of Conda, so its
# operations' asymptotic time complexities need not be optimal: nobody will
# have a million Conda environments that they activate and deactivate a billion
# times. Write code that is simple, easy to understand, and fast for any series
# of activations and deactivations when the number of environments is small,
# rather than code that minimizes asymptotic time complexity. Do document all
# time complexities, including of construction, either in the class docstring
# or in each relevant public method's docstring. Separately from that, ensure
# the simulator has a class docstring explaining how to use it, and doctests
# showing example usage. The doctests need not be nearly as extensive as the
# unittest tests here. Feel free to keep the module and class names simconda
# and Simulator, or to change them. (If you change the module name, change this
# test module name accordingly.)


# FIXME: Instances of the simulator are finite state machines. Make sure you
# understand why this is, and approximately how many vertices and edges are in
# the DFA state chart for a Simulator instance constructed with n names. Decide
# if it would be valuable to include such information in the documentation. If
# so, put it in an appropriate docstring (probably the simconda module
# docstring). But if you don't think this would be valuable, don't include it.


# FIXME: "We will have a million Conda environments and we will activate and
# deactivate them a billion times," the client says. "And in who knows what
# order. So we're going to need another version of the simulator."
#     You explain that running too slow in such a use is a feature, not a bug,
# because the actual conda command will run too slow, too. But the client is
# not having it. The whole point of the simulator, the client insists, is to
# find out what would eventually happen, not how long it would take to happen.
#     "Can you do it?"
#     "I guess," you hear yourself say. "I know a few ways to make activate and
# deactivate take O(1) time in any series of activations and deactivations, no
# matter how many environments exist or have been activated and deactivated so
# far, all while still using space linear in the number of environments."
#     "Excellent! A few... so, that's three ways, right? We'll take all three!"
#     "Three separate asymptotically optimal simconda.Simulator alternatives?"
#     "Yes," the client says, and you wish you actually had thought of at least
# one way to make activate and deactivate take O(1) time!
#     You think about the problem, and soon your mind wanders to other threes.
# Null, void, and of no effect. Misty, Brock, and Ash. Data structures you can
# readily implement yourself, already available ones you use all the time, and
# already available ones that are less often used and you may not be aware of.
#
# Name these three new simconda.py classes to reflect something about how each
# works; don't keep the names ScalableSimulator1, ScalableSimulator2, and
# ScalableSimulator3. They must pass the same unittest tests as Simulator, with
# no duplication of test code. I recommend adapting the existing test code so
# it is easy to add more implementations to be tested; then, for each of the
# "scalable" simulators, add it to be tested, check that its tests fail, then
# implement it and get all tests to pass. They should have doctests analogous
# to those written for Simconda (and for those, test logic may be duplicated).
# The new simulators should be able to handle
