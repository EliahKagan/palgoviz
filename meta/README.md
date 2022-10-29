# Meta - administrative work in progress

This directory contains material that is about work on the project rather than
the topics the project is about.

There is a continuum of how "meta" something is. Only the most meta things
should go here. We may not need this directory in the future.

(See "Contents" below for what is actually here.)

## Where to put things instead

Instead of putting things here, most material that feels like it is "about the
project" should instead go elsehwere. In particular:

- Documentation of interest to people using this project should go in a `doc/`
  directory if it does not belong in the top-level project `README.md` or any
  per-subdirectory readme file (or docstrings/comments).

- Plans and other notes about making exercises, how they may be grouped, the
  order in which it may make sense to do them, and other documentation that is
  of limited interest yet worth keeping, belongs in `notes/`. Once this rises
  to the level of broadly useful documentation, it may be better elsewhere, but
  still not here.

Note that the boundaries around what should go in the `meta/` directory are not
established. This subdirectory readme is just, like, my opinion.

## Contents

Right now, the only things here, besides this readme, are:

### `restructure`

This is a script that proposes, and should help to automate, a particular
restructuring/reorganization of the project's contents.

See the top-level project `README.md` for broad context on this, and the code
and comments in `restructure` for details of that particular proposal.

### `restructure.md`

These are instructions for using the `restructure` script. Note that the script
itself is documentation of *what* changes are proposed.

### `run-test-scripts`

This is a script that runs test-containing modules as script. It is a hackish
way of doing so. If it is improved, and turns out to be useful, then it should
be moved somewhere else.
