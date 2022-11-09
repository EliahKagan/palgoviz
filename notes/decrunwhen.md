# Decorators run once per decorated definition.

Decorators are only called when decorated functions are *defined*.

That's why, for a decorator to change the behavior of a decorated function when
the decorated function *runs*, the decorator must define and return a *wrapper
function*.

This works because decorating a function definition replaces the function you
write (which is passed as an argument to the decorator) with the function the
decorator returns.
