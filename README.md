# algoviz

This is a project to develop approaches and materials for teaching and learning
Python together with algorithms and data structures, with a substantial
component of visualization. The intended learner is (at least at this point)
expected to have substantial programming experience, but not necessarily any
experience in Python, and not necessarily any experience with algorithms and
data structures, other than the most basic topics such as using arrays.

Graphviz is heavily used for visualizations. Not all topics have visualizations
as demos or exercises that produce visualizations, and probably some never
will have them (since they may sometimes not be necessary or helpful), but it
is likely that most topics will have them.

---

**FIXME: This readme must be updated in light of the recent restructure.**

This is a work in progress. In particular, project structure is not yet
established, but the structure will be improved to be less flat. Most likely
it will not be useful to have wheels or conda packages built from it.

- The `conda-build` dependency is not needed yet, but the `conda develop`
  command it provides is likely to help during and after the project
  restructuring.

- Currently, most content is in `basics/`, including both basic and more
  advanced topics. Some notebooks have has been pulled out of `basics/` into
  `math/`. The `basics/` directory will likely go away when the project
  structure is changed, splitting into other directories, likely `algoviz/`
  for the `*.py` files other than test modules (so that the principal
  top-level package will be called `algoviz`), `tests/` for the tests,
  `notebooks/` for the `.ipynb` files, and some more minor directories. But
  this is not yet decided.

A license must still be added. This README file requires further revision, so
that it explains how to use the project. Most subdirectories should also have
README files, which is largely not yet done.

---

This project is somewhat related, though not closely tied to, a previous, less
ambitious project: https://github.com/EliahKagan/algorithms-suggestions

It is unknown how comprehensive this project will be, or whether it will become
a goal to produce materials that are ready-made for widespread use (rather than
requiring careful selection and customization). In particular, classroom use is
not currently a focus.
