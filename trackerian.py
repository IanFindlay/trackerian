#!/usr/bin/env/ python3

"""Trackerian - a command line time tracker."""

import argparse
import datetime
import pickle
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
    parser.add_argument('-s', '--summary', action='store_true',
                        help='print summary of tracked activities')

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
        self.start_str = str_format_datetime(self.start)
        self.end = None
        self.end_str = None
        self.duration = None

        Activity.instances.append(self)

    def __str__(self):
        name_just = self.name.ljust(15)
        if not self.end:
            return '({} - Tracking)  {} Duration: {}'.format(
                self.start_str, name_just,
                str(self.return_current_duration()).split('.')[0]
            )

        return '({} - {})  {} Duration: {}'.format(
            self.start_str, self.end_str, name_just,
            str(self.duration).split('.')[0]
        )

    def end_activity(self):
        """Set end and duration then print end confirmation."""
        print()
        if not self.end:
            self.end = get_current_time()
            self.end_str = str_format_datetime(self.end)
            self.duration = self.end - self.start
            print('Tracking of {} Finished \t Duration: {}'.format(
                self.name, str(self.duration).split('.')[0]
            ))
        else:
            print('Tracking of {} is already finished.'.format(self.name))
        print()

    def return_current_duration(self):
        """Calculate and return timedelta of activity time tracked so far."""
        current_time = get_current_time()
        return current_time - self.start


def get_current_time():
    """Return datetime object of the current time."""
    return datetime.datetime.now()


def str_format_datetime(datetime_object):
    """Format datetime object into string.

    Args:
        datetime_object (datetime): Datetime time object.

    Returns:
        String of datetime object formatted HH:MM:SS.

    """
    return datetime_object.strftime('%H:%M:%S')


def pickle_activities():
    """Write pickled Activity.instances to file."""
    with open('data.pickle', 'wb') as pickled_file:
        pickle.dump(Activity.instances, pickled_file)


def unpickle_activities():
    """Unpickle and return Activity instances from file.

    Returns:
        List of Activity instances.
    """
    with open('data.pickle', 'rb') as pickled_file:
        return pickle.load(pickled_file)


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
            print("No activities are currently being tracked.")

    if args['summary']:
        total_time = datetime.timedelta(0)
        for activity in Activity.instances:
            if activity.duration:
                total_time += activity.duration
            else:
                total_time += activity.return_current_duration()
        formatted_time = str(total_time).split('.')[0]
        print()
        print('Activities Tracked: {} | Total Time Tracked: {}'.format(
            len(Activity.instances), formatted_time), end='\n\n')
        for activity in Activity.instances:
            print(activity)
        print()


if __name__ == '__main__':
    # Load data from data.pickle or create it if missing
    try:
        Activity.instances = unpickle_activities()
    except FileNotFoundError:
        with open('data.pickle', 'w') as file_creator:
            pass

    main()
    pickle_activities()
