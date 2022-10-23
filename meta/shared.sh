# Shared logic for the restructure and patch-imports scripts.
#
# Both scripts use the die function, and both need the current-directory check,
# because while patch-imports is run by restructure, it can be run separately.

die() {
    printf '%s: error: %s\n' "$0" "$1" >&2
    exit 1
}

# We should be in the top-level repository directory.
[ -d .git ] || die 'not in repository root'
