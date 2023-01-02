# <!-- SPDX-License-Identifier: 0BSD -->

# Extra documentation

This `doc/` directory contains:

- Documentation that applies to the project as a whole but is not sufficiently
important to appear in the top-level readme.
- Supporting files for the top-level readme.


## Where to look instead

For the most important information about the project, see [**the top-level
readme**](../README.md).

For information about the contents of a particular directory, see the summary
in the top-level readme, or he more detailed `README.md` file in the directory
of interest.

The `palgoviz/` and `tests/` directories do not have their own readme files.
They are the main package (source code) directory and the directory that holds
tests, respectively, except that most doctests are in docstrings on functions
and classes and thus appear in `palgoviz/` rather than `tests/`.

## What’s actually here

Besides this `README.md` file, the files in this `doc/` directory are:

- `dist-readme.md` - The readme file intended for PyPI.
- `example.svg` - The visualization example shown (mainly) in the top-level
  readme.
