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
        print('Did not pass a filename')
        return 1
    with open('names.txt') as file: 
        for line in file:
            hello(line.strip()) 
    return 0 
        
if __name__ == '__main__':  # If we are running this module as a script.
    sys.exit(run()) # for exit codes in powershell, $LASTEXITCODE
