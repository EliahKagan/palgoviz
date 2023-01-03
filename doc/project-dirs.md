<!-- SPDX-License-Identifier: 0BSD -->

# Repository Table of Contents

The most important and interesting parts of this project are the
[`palgoviz/`](#palgoviz), [`tests/`](#tests), and [`notebooks/`](#notebooks)
directories.

Here’s a full list of directories:

## `palgoviz`

This directory, not to be confused with the top-level repository directory,
contains Python modules (`.py` files), other than test modules.

Note that many tests are actually in these modules, because many of the tests
in this project are doctests, which appear in module, function, and class
docstrings.

## `tests`

Separate tests. Most of these are `.py` files that contain tests using the
`unittest` framework. There are also a few `.txt` files containing extended
doctests.

<!-- TODO: When pytest test modules are added, expand the above paragraph. -->

## `notebooks`

These are Jupyter notebooks showcasing Python and algorithms concepts, and
often tying in with code in `palgoviz`.

## `math`

These are Jupyter notebooks, and supporting image files, for illustrating some
math concepts that are not specifically about code and that do not involve
using or discussing any of the code in the `palgoviz` package.

## `notes`

These are files with information potentially relevant to preparing exercises
from the code in this project. It currently also contains some documentation in
rough draft form.

## `doc`

This is project-wide documentation that is not important enough to go in this
top-level readme, and documentation support files (e.g., images).

## `sandbox`

This presents traditional and namespace packages and shows how they behave
differently.

## `meta`

This contains files that are more about project internals than about Python,
algorithms and data structures, or even *use* of the project. This directory
may go away in the future.
