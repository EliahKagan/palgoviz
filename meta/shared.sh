# Shared code for the restructure and patch-imports scripts.
#
# Both scripts use the functions. Both also need the directory check: usually
# patch-imports will be run by restructure, but it may also be run on is own.

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

# We should be in the top-level repository directory.
[ -d .git ] || die 'not in repository root'
