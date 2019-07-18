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
    parser.add_argument('-c', '--current', action='store_true',
                        help='print current status of activity tracking')

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
        return 'Tracking {} for {}.'.format(
            self.name, str(self.return_current_duration())
        )

    def end_activity(self):
        """Set end and duration then print end confirmation."""
        self.end = get_current_time()
        self.duration = self.end - self.start
        print('{} ended - duration was {}'.format(self.name, self.duration))

    def return_current_duration(self):
        """Calculate and return timedelta of activity time tracked so far."""
        current_time = get_current_time()
        return current_time - self.start


def get_current_time():
    """Return datetime object of the current time."""
    return datetime.datetime.now()


def main():
    """Coordinate creation and time tracking of activities."""
    args = parse_arguments(sys.argv[1:])
    if not args:
        sys.exit()

    if args['begin']:
        if Activity.instances and not Activity.instances[-1].end:
            Activity.instances[-1].end_activity()
        Activity(args['begin'])
        print(Activity.instances[-1])

    if args['finish']:
        try:
            Activity.instances[-1].end_activity()
        except IndexError:
            print("No activities have been tracked.")

    if args['current']:
        try:
            if Activity.instances[-1].end:
                print("Currently Not Tracking an Activity")
            else:
                print(Activity.instances[-1])
        except IndexError:
            print("No activities have been tracked.")


if __name__ == '__main__':
    main()
