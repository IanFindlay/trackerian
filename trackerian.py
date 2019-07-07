#!/usr/bin/env/ python3

"""Trackerian - a command line time tracker."""

import argparse
import sys

def parse_arguments(args):
    """."""
    parser = argparse.ArgumentParser(description="Commandline Time Tracker")
    parser.add_argument('-b', '--begin', help='starts timing a task')


    if not args:
        parser.print_help()
        sys.exit


    return vars(parser.parse_args(args))


def begin_activity():
    """."""
    pass

def main():
    """."""
    args = parse_arguments(sys.argv[1:])


if __name__ == '__main__':
    main()
