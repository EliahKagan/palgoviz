<!-- SPDX-License-Identifier: 0BSD -->

# Major Python topics not currently covered

This is a list of some major Python topics not, or not yet, covered in this
project:

- Manual `venv` (this project uses `conda`, or poetry which handles virtual
  environments automatically)
- Data classes (including `attrs`) and named tuples
- Type annotations and static type checking
- `Counter` and `defaultdict`
- `pytest` tests (rather than just as a test runner for other tests)
- `async` and `await`
- NumPy (though `notebooks/la_numpy.ipynb` as an extremely minimal skeleton)
- Requests

Note: The value in this list is its brevity. To prevent it from growing without
bound, only topics that *many if not most* Python programmers rely on and use
regularly should be added.
