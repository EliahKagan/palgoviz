# Shared code for the restructure and patch-imports scripts. Source this file
# to define helpers, check we are in the right place, and validate arguments.

msg() {
    printf '%s: %s\n' "$0" "$1" >&2
}

err() {
    msg "error: $1"
}

die() {
    err "$1"
    exit 1
}

# If passing "-b" to sed may not be supported, fail before making any changes.
sed --version | grep -qF '(GNU sed)' || die 'need sed to be GNU sed'

# This version doesn't support command-line args, so make sure there are none.
[ "$#" -eq 0 ] || die 'too many arguments'

# We should be in the top-level repository directory.
[ -d .git ] || die 'not in repository root'

# And this directory should be called algoviz.
[ "$(basename -- "$PWD")" = algoviz ] ||
    die 'current directory is not called algoviz'

# And its parent directory should NOT be called algoviz. If the user is
# accidentally in algoviz/algoviz, then there should be no .git directory, but
# this is simple and easy and safeguards against mistakes involving re-cloning.
[ "$(basename -- "$(dirname -- "$PWD")")" != algoviz ] ||
    die 'current directory is algoviz/algoviz but we want the parent'
