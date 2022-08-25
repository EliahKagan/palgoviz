"""Tests for the classes in simconda.py."""

# FIXME: Write unittest tests for simconda.Simulator, a class whose instances
# simulate the effect of conda's activate and deactivate commands on what Conda
# environment, if any, is active. This is more subtle than it may first appear,
# so you'll to do some experiments. Make several throwaway Conda environments
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
# one gives commands and queries which environment is currently active, but it
# is not required that you parse actual shell commands, and I recommend against
# doing so, since if the simulator offers a good object-oriented interface, a
# command-line interface could easily be built atop it if needed.
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
# and Simulator or to change them. (If you change the module name, change this
# test module name accordingly.)


# FIXME: Instances of the simulator are finite state machines. Make sure you
# understand why this is, and approximately how many vertices and edges are in
# the DFA state chart for a Simulator instance constructed with n names. Decide
# if it would be valuable to include such information in the documentation. If
# so, put it in an appropriate docstring (probably the simconda module
# docstring). But if you don't think this would be valuable, don't include it.
