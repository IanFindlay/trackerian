#!/usr/bin/env/ python3

"""Trackerian - a command line time tracker."""

import argparse
import datetime
import sys


def parse_arguments(args):
    """."""
    parser = argparse.ArgumentParser(description="Commandline Time Tracker")
    parser.add_argument('-b', '--begin', help='starts timing a task')
    parser.add_argument('-f', '--finish', action='store_true',
                        help='finished timing a task')

    if not args:
        parser.print_help()
        sys.exit()

    return vars(parser.parse_args(args))


class Activity():
    """."""
    instances = []

    def __init__(self, name):
        self.name = name
        self.start = get_current_time()

        Activity.instances.append(self)


def get_current_time():
    """Return current time datetime object."""
    return datetime.datetime.now()


def main():
    """."""
    args = parse_arguments(sys.argv[1:])
    if args['begin']:
        Activity(args['begin'])


if __name__ == '__main__':
    main()
