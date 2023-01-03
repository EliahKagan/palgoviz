<!-- SPDX-License-Identifier: 0BSD -->

# Running Tests

## In Visual Studio Code

`.vscode/settings.json` has some useful configuration, including for running
tests using VS Code’s test runner interface (the “beaker” icon on the activity
bar on the left). This configuration uses the `pytest` test runner, which is
capable of running all tests in the project. This should just work
automatically.

Make sure to tell it that this project uses the `palgoviz` conda environment,
or verify that it has detected this. That also applies to other IDEs.

If VS Code asks to install `pytest` or otherwise claims that it needs to be
installed, you should decline, and double check that VS Code is really using
the `palgoviz` environment.

## From the command line: `pytest`

Tests can be run from VS Code or another IDE, but you may want to run them from
a terminal (and they may run faster that way, too).

1. Make sure you are in the top-level repository directory.

2. Activate the `palgoviz` environment in your terminal (if not already done).
   To do this, if you’re using `conda`, run:

    ```sh
    conda activate palgoviz
    ```

    Or if you're using `poetry`, run:

    ```sh
    poetry shell
    ```

3. Run the tests:

    ```sh
    pytest --doctest-modules
    ```

    The `--doctest-modules` option causes it to include doctests present in
    modules. It does not cause any tests to be omitted. That command runs all
    tests in the project, including but not limited to doctests.

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
