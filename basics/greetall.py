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
    match len(sys.argv):
        case 1:
            print(f'ERROR in {sys.argv[0]}: Did not pass a filename', file=sys.stderr)
            return 1
        case 2:
            pass
        case _:
            print(f'WARNING in {sys.argv[0]}: Too many arguments, see doctring for usage', file=sys.stderr)    
    
    name = sys.argv[1]

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
