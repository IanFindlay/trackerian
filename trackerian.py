#!/usr/bin/env/ python3

"""Trackerian - a command line time tracker."""

import argparse
import datetime
import sys


def parse_arguments(args):
    """Parse arguments and return them in a dictionary.

    Args:
        args (list): List of arguments and associated values to parse.

    Returns:
        None if args argument evaluates to False.

        Dictionary of arguments and their post-parsed values.

    """
    parser = argparse.ArgumentParser(description="Command Line Time Tracker")
    parser.add_argument('-b', '--begin', metavar='activity',
                        help='begin timing a task')
    parser.add_argument('-f', '--finish', action='store_true',
                        help='finish timing a task')

    if not args:
        parser.print_help()
        return None

    return vars(parser.parse_args(args))


class Activity:
    """Class representing an activity.

        Attributes:
            instances (list): Class attribute to track instantiated members.

            name (str): Name of the activity.
            start (datetime): Time activity started (instantiated).
            end (datetime): Time activity ended (end_activity method).
            duration (timedelta): Time difference between start and end.

    """
    instances = []

    def __init__(self, name):
        """Initialise member of Activity class.

        Args:
            name (str): Name of the activity.

        """
        self.name = name
        self.start = get_current_time()
        self.end = None
        self.duration = None

        Activity.instances.append(self)

    def __str__(self):
        return '{} currently being tracked.'.format(self.name)

    def end_activity(self):
        """Set end and duration then print end confirmation."""
        self.end = get_current_time()
        self.duration = self.end - self.start
        print('{} ended - duration was {}'.format(self.name, self.duration))


def get_current_time():
    """Return datetime object of the current time."""
    return datetime.datetime.now()


def main():
    """Coordinate creation and time tracking of activities."""
    args = parse_arguments(sys.argv[1:])
    if not args:
        sys.exit()

    if args['begin']:
        Activity(args['begin'])
        print(Activity.instances[-1])

    if args['finish']:
        Activity.instances[-1].end_activity()


if __name__ == '__main__':
    main()
