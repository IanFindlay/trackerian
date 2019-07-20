#!/usr/bin/env/ python3

"""Trackerian - a command line time tracker."""

import argparse
import collections
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
                        help='begin timing an activity')
    parser.add_argument('-c', '--current', action='store_true',
                        help='print status of current activity')
    parser.add_argument('-f', '--finish', action='store_true',
                        help='finish timing an activity')
    parser.add_argument('-l', '--list', action='store_true',
                        help='list tasks')
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
        if not self.end:
            return '({} - Tracking)  {:<15} Duration: {}'.format(
                self.start_str, self.name,
                str_format_timedelta(self.return_current_duration())
            )

        return '({} - {})  {:<15} Duration: {}'.format(
            self.start_str, self.end_str, self.name,
            str_format_timedelta(self.duration)
        )

    def end_activity(self):
        """Set end and duration then print end confirmation."""
        print()
        if not self.end:
            self.end = get_current_time()
            self.end_str = str_format_datetime(self.end)
            self.duration = self.end - self.start
            print('Tracking of {} Finished \t Duration: {}'.format(
                self.name, str_format_timedelta(self.duration)
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
    """Return formatted datetime object string.

    Args:
        datetime_object (datetime): Datetime time object.

    Returns:
        Str of datetime object formatted HH:MM:SS.

    """
    return datetime_object.strftime('%H:%M:%S')


def str_format_timedelta(timedelta_object):
    """Return formatted and trimmed timedelta object.

    Args:
        timedelta_object (timedelta): Datetime.timedelta object.

    Returns:
        Str of timedelta object formatted HH:MM:SS.
    """
    trimmed = str(timedelta_object).split('.')[0]
    if len(trimmed) == 7:
        return '0{}'.format(trimmed)
    return trimmed


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


def print_summary():
    """Print summary of tracked activities (Total and Grouped)."""
    activity_durations = collections.defaultdict(datetime.timedelta)
    for activity in Activity.instances:
        if activity.duration:
            duration_to_add = activity.duration
        else:
            duration_to_add = activity.return_current_duration()

        activity_durations['total'] += duration_to_add
        activity_durations[activity.name] += duration_to_add

    formatted_time = str_format_timedelta(activity_durations['total'])
    print('Activities Tracked: {} | Total Time Tracked: {}'.format(
        len(Activity.instances), formatted_time
    ))
    print()

    del activity_durations['total']
    sort = sorted(activity_durations.items(), key=lambda x: x[1], reverse=True)
    for activity, duration in sort:
        print("{:<15}: {}".format(activity, str_format_timedelta(duration)))


def main():
    """Coordinate creation and time tracking of activities."""
    args = parse_arguments(sys.argv[1:])
    if not args:
        sys.exit()

    print()

    if args['begin']:
        if Activity.instances and not Activity.instances[-1].end:
            Activity.instances[-1].end_activity()
        Activity(args['begin'])
        print(Activity.instances[-1])

    elif args['current']:
        try:
            if Activity.instances[-1].end:
                print("Currently Not Tracking an Activity")
            else:
                print(Activity.instances[-1])
        except IndexError:
            print("No activities are currently being tracked.")

    elif args['finish']:
        try:
            Activity.instances[-1].end_activity()
        except IndexError:
            print("No activities have been tracked.")

    elif args['list']:
        for num, activity in enumerate(Activity.instances):
            print("{:<2}| {}".format(num, activity))

    elif args['summary']:
        print_summary()

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
