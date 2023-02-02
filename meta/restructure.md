<!-- SPDX-License-Identifier: 0BSD -->

# Usage suggestions for `restructure`

To restructure a “stable” branch—one that is not a feature branch off a “trunk”
that has been, or ought to be, restructured—do this:

 1. Switch to the branch.

 2. Run `isort`, `flake8`, and all tests. There should be no problems yet.

 3. Run `meta/restructure full-with-nb` and inspect the results.

 4. If the `algoviz` conda environment for the restructured project is not set
    up yet on your machine, do that. As the script output mentions, after
    activating it the first time, make sure you are in the root of the
    repository, and run: `pip install -e .`

    Do not run that command in the wrong directory, or modules will be found in
    places they shouldn’t be, which will both cause and mask bugs. That command
    only needs to be run once (per machine, unless you delete the environment).

 5. Run all tests. Ensure all three test runners we use are working.

 6. Stage the changes.

 7. Run `isort` (it will consoldate new `from` imports) and flake8.

 8. Inspect and run all notebooks. Fix anything broken. Alhough `full-with-nb`
    was used, there may be manual work to do. Save notebooks if they have input
    (code) or Markdown cell changes or important output changes.

 9. Go through all `*.py` files. Examine all docstrings and comments. Fix
    outdated references and any other inaccuracies. (This and step 8 can be
    done in either order or interleaved.)

10. If not already done, update the project’s top-level `README.md` to reflect
    the new structure and say how to open the project, run tests, and use
    notebooks.

Then, given a “stable” branch that was restructured, and a feature branch:

 1. Switch to the feature branch.

 2. If not already done, merge from the last commit in the history of the
    stable branch from *before* that branch was restructured.

 3. Run `isort`, `flake8`, and all tests. There should be no problems yet.

 4. Run `meta/restructure full-no-nb` and inspect the results.

 5. Inspect the results. Run all tests. Fix anything that is broken.

 6. Run isort to normalize imports. Re-run tests. All should still pass.

 7. Commit these changes (but don’t push). This prepares for the merge.

 8. Merge from the stable branch.

 9. Re-run tests. Fix any problems, updating any `*.py` that are no longer
    correct, due to the change in project structure. This is mainly docstrings
    and comments in code introduced on the feature branch.

10. Commit these changes (but don’t push).

11. Update `*.ipynb` files that weren’t updated in the merge. It may help to
    run `meta/restructure imports-with-nb` at this point. But at minimum, all
    notebooks, even if unchanged, be re-run and inspected. Notebooks have
    changed should be saved. Those that have not shouldn’t, to avoid merge
    conflicts when multiple feature branches are merged back in.

12. Commit and push.

For feature branches *of* feature branches, that may be followed, but if the
changes are very small, it *may* be sufficient simply to merge normally.
