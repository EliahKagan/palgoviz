<!-- SPDX-License-Identifier: 0BSD -->

# Installation - Conda

## Getting `conda`

If you don’t have
[`conda`](https://en.wikipedia.org/wiki/Conda_(package_manager)) already, we
suggest [**Miniforge**](https://github.com/conda-forge/miniforge), which is
what we’re using.

If you already have `conda` through another distribution, such as
[Miniconda](https://docs.conda.io/en/latest/miniconda.html) or
[Anaconda](https://www.anaconda.com/), that should be fine. (The
`environment.yml` file states the channel explicitly, rather than relying on
channel defaults that vary across distributions.)

## Optional: Using `mamba`

All the following `conda` commands can be run with `mamba` instead of `conda`
[if you have `mamba`
installed](https://mamba.readthedocs.io/en/latest/installation.html).

The exception is that, on Windows, `conda activate` and `conda deactivate` must
still be used, due to [limitations in `mamba` PowerShell
integration](https://github.com/mamba-org/mamba/issues/1717).

For commands that create and update the environment, `mamba` may be faster than
`conda`.

## Creating and using the environment

To obtain and set up palgoviz:

1. Clone the repository:

    ```sh
    git clone https://github.com/EliahKagan/palgoviz.git
    ```

    If you forked the repository, which you [may want to
    do](https://docs.github.com/en/get-started/quickstart/fork-a-repo), then
    use your fork’s URL instead.

2. Go into the top-level project directory:

    ```sh
    cd palgoviz
    ```

3. Create the `conda` environment:

    ```sh
    conda env create
    ```

4. Activate the environment:

    ```sh
    conda activate palgoviz
    ```

    You must activate the environment each time you use the project in a new
    shell (or after deactivating it).

5. Create an “editable install” in the environment:

    ```sh
    pip install -e .
    ```

    That command only has to be run once (unless you delete and recreate the
    environment). It does *not* need to be run each time you use the project.

    This step is required to allow some modules to be run as scripts, and to be
    run from any location. Most of the project will work without it, but a
    small amount of functionality, and tests for that functionality, will fail
    without it.

    If you have `conda-build` installed, you can use `conda develop .` instead
    of `pip install -e .`, if you like.

## Updating the environment

If you’ve just installed the project, then it is already up to date (for now).
The following instructions are for later.

At this time, most project dependencies are not pinned in `environment.yml`,
and dependencies may continue to change as work proceeds further on the
project. (See “Pinning note” below.)

The following is recommended for updating the project.

1. Activate the environment if it is not already active:

    ```sh
    conda activate palgoviz
    ```

2. Update packages currently installed in the environment:

    ```sh
    conda update --all
    ```

3. Make sure you are in the top-level directory. That is the directory that
   contains the project-wide `README` and `environment.yml` files.

4. Install any new project dependencies, and remove any old dependencies that
   are known to no longer be needed:

   ```sh
   conda env update --prune
   ```

## Pinning note

We are not currently pinning specific package versions, nor listing indirect
dependencies, in `environment.yml`.

If you want dependencies pinned to specific known-working versions, you can
[install with `poetry`](install-with-poetry.md) instead of with `conda`.
