#!/usr/bin/env pwsh

# Copyright (c) 2022 Eliah Kagan
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

# This script runs Python modules as scripts when they look like they are meant
# to be run that way as a way of running unit tests they contain. This is for
# testing that it works to run them this way.
#
# This script is for Windows systems. It should also work on Unix-like systems
# (if PowerShell is installed), but it won't check that files that should be
# marked executable (for easy use on *nix) actually are. On Unix-like systems,
# it is better to use the Bash script run-test-scripts (no file extension).
#
# NOTE: This is a rough draft. Possible areas of improvement are revealed by:
#
#   Invoke-ScriptAnalyzer meta/run-test-scripts.ps1


Set-StrictMode -Version Latest

function Search($Pattern) {
    $line_pattern = "^[ ]{4}${Pattern}[ ]*\r?$"
    git grep --untracked --name-only -P $line_pattern
}

function Run-Matches($Label, $Pattern, $Arguments) {
    Write-Output "`nRunning scripts for ${Label}:`n`n"

    foreach ($file in search($Pattern)) {
        python $file $Arguments
    }
}

Run-Matches -Label 'unittest tests' -Pattern 'unittest[.]main[(][)]' -q $args
Run-Matches -Label 'doctests' -Pattern 'doctest[.]testmod[(][)]' $args
