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
    # open file named "name"
    file = open(name)
    # greet each name (probably some kind of loop here)
    for line in file: 
        hello(line.strip())
    # close the file
    file.close()
        
if __name__ == '__main__':  # If we are running this module as a script.
    sys.exit(run())
