#!/usr/bin/env/ python3

"""Trackerian - a command line time tracker."""

import argparse
import datetime
import sys


def parse_arguments(args):
    """."""
    parser = argparse.ArgumentParser(description="Commandline Time Tracker")
    parser.add_argument('-b', '--begin', metavar='activity',
                        help='begin timing a task')
    parser.add_argument('-f', '--finish', action='store_true',
                        help='finish timing a task')

    if not args:
        parser.print_help()
        return None

    return vars(parser.parse_args(args))


class Activity():
    """."""
    instances = []

    def __init__(self, name):
        self.name = name
        self.start = get_current_time()
        self.endtime = None
        self.duration = None

        Activity.instances.append(self)

    def end_activity(self):
        """."""
        self.endtime = get_current_time()
        self.duration = self.endtime - self.start


def get_current_time():
    """Return current time datetime object."""
    return datetime.datetime.now()


def main():
    """."""
    args = parse_arguments(sys.argv[1:])
    if not args:
        sys.exit()

    if args['begin']:
        Activity(args['begin'])

    if args['finish']:
        Activity.instances[-1].end_activity()


if __name__ == '__main__':
    main()
