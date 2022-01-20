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
    # Uses LBYL (look before you leap).
    # block comments, (VSCODE) control + K + C, uncomment control+K+U
    match sys.argv:
        case (command,):
            print(f'ERROR in {command}: Did not pass a filename', file=sys.stderr)
            return 1
        case (command, name):
            pass
        case (command, name, *_):
            print(f'WARNING in {command}: Too many arguments, see doctring for usage', file=sys.stderr)

    # Uses EAFP (easier to ask forgiveness than permission).
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
