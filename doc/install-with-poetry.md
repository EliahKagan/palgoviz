<!-- SPDX-License-Identifier: 0BSD -->

# Installation - Poetry

If you don’t have [`poetry`](https://python-poetry.org/) already, you can
install it by following [the official
instructions](https://python-poetry.org/docs/#installation).

## First, you need Python

Note that palgoviz currently only supports Python 3.11. Unlike
[`conda`](install-with-conda.md), `poetry` does not directly facilitate
installing Python itself. Depending on what version of Python you already have
installed, if any, you may need [to install Python](https://wiki.python.org/moin/BeginnersGuide/Download) first.

Those instructions for installing Python are not specifically for 3.11. [The
“Linux”
instructions](https://wiki.python.org/moin/BeginnersGuide/Download#Linux) may
or may not give you that version. On some systems, Python 3.11 is available,
but provided by a `python3.11` package rather than a `python` or `python3`
package.

If you are using an Ubuntu release without a `python3.11` package, you can use
the [deadsnakes PPA](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa) to
install it.

## Installing Poetry

Once you have Python, you can install Poetry.

Either the [official
installer](https://python-poetry.org/docs/#installing-with-the-official-installer)
or [`pipx`](https://python-poetry.org/docs/#installing-with-pipx) should work
well.

## Installing Graphviz

palgoviz depends on an external
[Graphviz](https://en.wikipedia.org/wiki/Graphviz) installation, since the
`graphviz` library it uses calls Graphviz executables, such as `dot` (called
`dot.exe` on Windows). The Python libraries this project depends on, including
the [`graphviz` *library*](https://pypi.org/project/graphviz/), are
automatically computed and obtained by `poetry`. But unlike
[`conda`](install-with-conda.md), `poetry` does not directly facilitate
installing *Graphviz itself*.

You can get Graphviz from [the official website](https://graphviz.org/) or
install it through a package manager.

With a package manager, the package name is often `graphviz`. This is the case
on Debian and its derivatives, and some other systems. On some systems, running
a command that is part of Graphviz, such as `dot`, will automatically inform
you that Graphviz is not installed and how to install it.

If you want to use a package manager to install Graphviz on Windows, you can
use [`scoop`](https://scoop.sh/). The package name is `graphviz`.

## Creating and using the virtual environment

To obtain and set up palgoviz:

1. Clone the repository:

    ```sh
    git clone https://github.com/EliahKagan/palgoviz.git
    ```

2. Go into the top-level project directory:

    ```sh
    cd palgoviz
    ```

3. Automatically create a `poetry`-managed virtual environment and install
   palgoviz and its dependencies into it, by running the single command:

    ```sh
    poetry install
    ```

4. Run a shell in which the virtual environment `poetry` created is
   automatically activated:

   ```sh
   poetry shell
   ```

   This is the only step you have to do each time you want to use palgoviz. The
   other steps, you only need to do once. When you run `poetry shell`, you
   should make sure to do so from the root of the repository (the top-level
   `palgoviz` directory that contains `pyproject.toml`).

## Updating dependencies

If you’ve just installed the project, then it is already up to date (for now).
The following instructions are for later.

### We update them periodically

When using `poetry`, exact versions of all direct and indirect dependencies are
pinned in `poetry.lock`. This file is committed as part of the repository and
we update it periodically, so if you are pulling changes from our repository,
then you will probably find it sufficient simply to run `poetry install` again
after doing so.

### Troubleshooting

The above approach will probably work fine, but if you have trouble, you can delete
`poetry.lock` and regenerate it. (One way to do that is just to attempt `poetry
install` again after deleting it. Running `poetry` and passing no arguments
lists available commands, including other ways to do this.)

### If you want to update them yourself

If you want to update all dependencies to the latest versions, including
versions newer than `pyproject.toml` specifies, you can run:

```sh
poetry up --latest
```

That modifies both `pyproject.toml` and `poetry.lock`.

Note that **`poetry` does not ship with the `up` action.** Instead, you must
install [poetry-plugin-up](https://github.com/MousaZeidBaker/poetry-plugin-up).
How you should do this [depends on how you installed
`poetry`](https://github.com/MousaZeidBaker/poetry-plugin-up#installation).

## The alternative to `poetry`

palgoviz can also be [installed with `conda` or
`mamba`](install-with-conda.md), which is what we usually do. We do not
currently pin specific package versions in `environment.yml`, but if you don’t
need that, then you may prefer to use `conda`/`mamba`, especially if you don’t
want to have to bother making sure Python 3.11 and Graphviz are externally
available (since `conda`/`mamba` will install those in the Conda environment,
along with the Python library dependencies).
