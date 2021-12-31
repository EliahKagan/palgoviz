#!/usr/bin/env python

"""
Greets multiple users from a file.

Usage:

    greetall FILENAME

"""

import sys

from greet import hello


def run():
    """Run the script."""
    try:
        name = sys.argv[1]
    except IndexError: 
        print(f'ERROR in {sys.argv[0]}: Did not pass a filename', file=sys.stderr)
        return 1
    try:
        with open(name, encoding='utf-8') as file: 
            for line in file:
                hello(line.strip()) 
    except OSError as error:
        print(f'ERROR in {sys.argv[0]}: {error}', file=sys.stderr)
        return 1
    return 0 
        
if __name__ == '__main__':  # If we are running this module as a script.
    sys.exit(run()) # for exit codes in powershell, $LASTEXITCODE
