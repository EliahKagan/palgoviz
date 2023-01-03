<!-- SPDX-License-Identifier: 0BSD -->

# Major Python topics not currently covered

This is a list of some major Python topics not, or not yet, covered in this
project:

- `venv` (this project uses `conda` instead of Python virtual environments)
- Data classes (including `attrs`) and named tuples
- Type annotations and static type checking
- `Counter` and `defaultdict`
- `pytest` tests (rather than just as a test runner for other tests)
- `async` and `await`
- NumPy
- Requests

Note: The value in this list is its brevity. To prevent it from growing without
bound, only topics that *many if not most* Python programmers rely on and use
regularly should be added.
