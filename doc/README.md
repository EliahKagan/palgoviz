<!-- SPDX-License-Identifier: 0BSD -->

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

- `install-with-conda.md` - Using `conda` or `mamba` to install palgoviz and
  keep its dependencies up to date.

- `install-with-poetry.md` - Using `poetry` to install palgoviz and keep its
  dependencies up to date.

- `project-dirs.md` - Brief descriptions of all interesting subdirectories of
  the top-level repository directory.

- `running-tests.md` - Details on running automated tests, going somewhat
  beyond the information in the top-level readme.

- `using-notebooks.md` - Detailed documentation on using the notebooks. Covers
real-time collaboration and the advantages/disadvantages of using the notebooks
in VS Code rather than JupyterLab.
