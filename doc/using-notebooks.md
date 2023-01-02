<!-- SPDX-License-Identifier: 0BSD -->

# Using the Notebooks

## JupyterLab

JupyterLab is installed as a dependency of the project, and all notebooks are
tested in it. First activate the `palgoviz` Conda environment in your terminal
if you haven’t already:

```sh
conda activate palgoviz
```

It is best to run JupyterLab from the top-level directory. If you installed
with `conda` but decided to skip the `conda develop` installation step, then
you must run it from there; otherwise, it is merely recommended.

To run JupyterLab:

```sh
jupyter lab
```

## Real-time collaboration, on notebooks

The nature of this project is such that it may be useful to collaborate in real
time to explore it, rework parts of is as exercises, or expand it. For example,
this may facilitate cooperative learning or tutoring.

We tested the notebooks extensively, and developed many of them, using the
[Real Time
Collaboration](https://jupyterlab.readthedocs.io/en/stable/user/rtc.html)
feature of JupyterLab.

In simple use, this is done by running

```sh
jupyter lab --collaborative --ip ADDRESS
```

where `ADDRESS` is replaced by *your* IP address on the network interface
through which your machine is accessible from the outside, and then sharing the
link with collaborators.

<!-- FIXME: There should probably be more, or less, detail above. -->

## Real-time collaboration, on modules

You can use JupyterLab Real Time Collaboration for other kinds of files than
notebooks, but if you use some other IDE, you should check if it offers such a
feature of its own.

In particular, Visual Studio Code has [Visual Studio Live
Share](https://visualstudio.microsoft.com/services/live-share/). We used this
to develop substantial parts of this project. It was also a major part of how
we reimplemented and discussed most of the code in the `palgoviz` package to
check that it was in good shape to be (re)worked as exercises.

## Notebooks in VS Code

When using VS Code to work with other parts of the project, it is convenient to
edit notebooks in VS Code as well. Furthermore, these days that seems to work
pretty well with Live Share.

<!-- FIXME: Verify and expand above: link to info on VSLS Jupyter features. -->

The biggest hurdle is cells that are *intended* to raise an unhandled
exception. When running multiple cells in a notebook (for example, the whole
notebook), JupyterLab heeds the `raises-exception` cell tag, printing a
traceback but continuing execution with the next cell. In contrast, the
`vscode-jupyter` extension does not yet do so.

Eventually this will be fully fixed in `vscode-jupyter`, at which point VS Code
may become the best way to work with the notebooks in this project. This is
related to
[microsoft/vscode-jupyter#11441](https://github.com/microsoft/vscode-jupyter/issues/11441).
