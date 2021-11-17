#!/usr/bin/env python3
#
#
import sys

def isForce():
    for argument in sys.argv:
        if (argument == 'force'):
            print("Forcing generation of new graph.")
            return True
    return False

def lastDays():
    for argument in sys.argv:
        try:
            return int(argument)
        except ValueError:
            pass
    return -1
