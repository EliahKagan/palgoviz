<!-- SPDX-License-Identifier: 0BSD -->

<!-- Rare case where trailing punctuation makes a heading clearer. -->
<!-- markdownlint-capture -->
<!-- markdownlint-disable MD026 -->
# Decorators run once per decorated definition.
<!-- markdownlint-restore -->

Decorators are only called when decorated functions are *defined*.

That's why, for a decorator to change the behavior of a decorated function when
the decorated function *runs*, the decorator must define and return a *wrapper
function*.

This works because decorating a function definition replaces the function you
write (which is passed as an argument to the decorator) with the function the
decorator returns.
