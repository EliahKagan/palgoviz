# algoviz

This is a project to develop approaches and materials for teaching and learning
Python together with algorithms and data structures, with a substantial
component of visualization. The intended learner is (at least at this point)
expected to have substantial programming experience, but not necessarily any
experience in Python, and not necessarily any experience with algorithms and
data structures, other than the most basic topics such as using arrays.

Graphviz is heavily used for visualizations. Not all topics have visualizatons
as demos or exercises that produce visualizations, and probably some never
will have them (since they may sometimes not be necessary or helpful), but it
is likely that most topics will have them.

This is a rough work in progress. In particular, project structure is not yet
established. (Relatedly, the project is not yet in good shape to have wheels
built from it, and it is not yet decided how many packages, if any, shoul be
generated from it.)

Currently most of the content is in `basics/`, including both basic and more
advanced topics. Material is being gradually pulled out of `basics/` to
top-level directories, but right now the only one that exists is `math/`.
Eventually, either much of what is currently in `basics/` will go in other
top-level directories, or `basics/` will be renamed, or the project structure
will change altogher so nothing corresponding to it even exists (maybe even
basic topics will be split out into multiple top-level directories, or maybe
the directory structure will become flatter or markedly more nested).

**This README file is itself a work in progress, may contain inaccuracies, and
does not necessarily represent a consensus or plan of project contributors.**
Also, top-level directories should have their own README files, but those are
not yet written, even in draft.

This project is somewhat related, though not closely tied to, a previous, less
ambitious project: https://github.com/EliahKagan/algorithms-suggestions

It is unknown how comprehensive this project will be, or whether it will become
a goal to produce materials that are ready-made for widespread use (rather than
requiring careful selection and customization). In particular, classroom use is
not currently a focus.
