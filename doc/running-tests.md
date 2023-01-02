<!-- SPDX-License-Identifier: 0BSD -->

# Running Tests

## In Visual Studio Code

`.vscode/settings.json` has some useful configuration, including for running
tests using its test runner interface (the “beaker” icon on the activity bar on
the left). This configuration uses the `pytest` test runner, which is capable
of running all tests in the project.

Make sure to tell it that this project uses the `palgoviz` conda environment,
or verify that it has detected this. That also applies to other IDEs.

## From the command line: `pytest`

Tests can be run from VS Code or another IDE, but you may want to run them from
a terminal (and they may run faster that way, too).

To do that, first activate the `palgoviz` Conda environment in your terminal if
you haven’t already:

```sh
conda activate palgoviz
```

Make sure you are in the top-level directory (the directory that contains this
`README.md` file). Then run:

```sh
pytest --doctest-modules
```

## From the command line: other test runners

Only the `pytest` test runner will run *all* tests in the project, but if you
want to use the `unittest` test runner to run the `unittest` tests, you can:

```sh
python -m unittest
```

If you want to use the `doctest` test runner to run the doctests, you can:

```sh
python -m doctest palgoviz/*.py tests/*.py tests/*.txt
```

That command is for a Unix-style shell. If you’re using Windows, you’re
probably in PowerShell and should use:

```sh
python -m doctest (gci palgoviz/*.py) (gci tests/*.py) (gci tests/*.txt)
```

The other commands are the same.
