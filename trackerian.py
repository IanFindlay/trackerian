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
        Dictionary of arguments and their post-parsed values.

    """
    parser = argparse.ArgumentParser(
        description="Command Line Time Tracker",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('-b', '--begin', metavar='activity', nargs='*',
                        help="Begin timing an activity with argument name")

    parser.add_argument('-c', '--current', action='store_true',
                        help="Print current tracking status")

    parser.add_argument('-f', '--finish', action='store_true',
                        help="Finish timing the current activity")

    parser.add_argument('-l', '--list', nargs='?',
                        choices=['all', 'day', 'week'], const='day',
                        help="Print list of tracked activities")

    parser.add_argument('-s', '--summary', nargs='?',
                        choices=['all', 'day', 'week'], const='day',
                        help="Print summary of today's activties or all")

    parser.add_argument('-t', '--tag', metavar='tag', nargs='*',
                        help="Add one word tag(s) to latest activity")

    parser.add_argument('-e', '--edit', nargs='*',
                        help="Edit a tracked activity with args:\n"
                        "{number} {category} {new value(s)}\n"
                        "Example: --edit 1 name New")

    if not args:
        parser.print_help()

    return vars(parser.parse_args(args))


class Activity:
    """Class representing an activity.

        Attributes:
            instances (list): Class attribute to track instantiated members.

            name (str): Name of the activity.
            tags (list): List of tags associated with the tag.
            start (datetime): Time activity began (instantiated).
            start_str (str): String representation of time activity began.
            end (datetime): Time activity finished (end_activity method).
            end_str (str): String representation of time activity finished.
            duration (timedelta): Time difference between start and end.

    """
    instances = []

    def __init__(self, name):
        """Initialise member of Activity class.

        Args:
            name (str): Name of the activity.

        """
        self.name = name.title()
        self.tags = []
        self.start = get_current_datetime()
        self.start_str = self.start.strftime('%H:%M:%S')
        self.end = None
        self.end_str = None
        self.duration = None

        Activity.instances.append(self)

    def __str__(self):
        if not self.end:
            return '({} - Tracking)  {:<20} Duration: {:<10} {}'.format(
                self.start_str, self.name,
                str_format_timedelta(self.return_current_duration()),
                ", ".join(self.tags)
            )

        return '({} - {})  {:<20} Duration: {:<10} {}'.format(
            self.start_str, self.end_str, self.name,
            str_format_timedelta(self.duration),
            ", ".join(self.tags)
        )

    def end_activity(self):
        """Set end and duration then print end confirmation."""
        print()
        if not self.end:
            self.end = get_current_datetime()
            self.end_str = self.end.strftime('%H:%M:%S')
            self.duration = self.end - self.start
            print('Tracking of {} Finished \t Duration: {}'.format(
                self.name, str_format_timedelta(self.duration)
            ))
        else:
            print('Tracking of {} is already finished.'.format(self.name))
        print()

    def return_current_duration(self):
        """Calculate and return timedelta of activity time tracked so far."""
        current_time = get_current_datetime()
        return current_time - self.start

    def update_datetime(self, to_edit, new_value):
        """Update a datetime value with a new value and update related values.

        Args:
            new_value (str): String of a time formatted HH:MM:SS.
            to_edit (str): Indicates which attribute to update.
        """
        hours, minutes, seconds = [int(x) for x in new_value.split(':')]
        if to_edit == 'start':
            self.start = self.start.replace(
                hour=hours, minute=minutes, second=seconds, microsecond=0
            )
            self.start_str = new_value

        elif to_edit == 'end':
            self.end = self.start.replace(
                hour=hours, minute=minutes, second=seconds, microsecond=0
            )
            self.end_str = new_value

        self.duration = self.end - self.start


def get_current_datetime():
    """Return datetime object of the current time."""
    return datetime.datetime.now()


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


def calculate_date_range_start(time_period):
    """Return earliest date that would be within the give time period.

    Args:
        time_period (str): String indicating the length of the period.

    Returns:
        None if time_period is 'all'.
        datetime object of start of the current day if time_period is 'day'.

    """
    if time_period == 'all':
        return None

    day_start_hour = 4
    day_start_minute = 0
    today = get_current_datetime()
    day_start = today.replace(hour=day_start_hour, minute=day_start_minute)

    if time_period == 'day':
        return day_start

    return day_start - datetime.timedelta(days=7)


def print_list(date_range_start):
    """Print enumerated list of tracked activities since date_range_start.

    Args:
        date_range_start (Datetime): Datetime object. Defaults to None.
        Activities with start datetimes earlier than this are enumerated
        but not printed.
    """
    for num, activity in enumerate(Activity.instances):
        if not date_range_start or activity.start >= date_range_start:
            print("{:<5} {}".format(num, activity))
            print()


def print_summary(date_range_start):
    """Print summary of tracked activities.

    Activities and their total durations are grouped by name and,
    in a separate display, by their tags.
    Only activities with datetimes later than date_range_start arg are used.

    Args:
        date_range_start (Datetime): Datetime object. Defaults to None.
            Sets the early end of the date range. Activities whose
            start datetimes are earlier than this will not be used in
            calculations or displayed.

    """
    activity_durations = collections.defaultdict(datetime.timedelta)
    tag_durations = collections.defaultdict(datetime.timedelta)

    total_time = datetime.timedelta()

    for activity in Activity.instances:
        if date_range_start and activity.start <= date_range_start:
            continue
        if activity.duration:
            duration_to_add = activity.duration
        else:
            duration_to_add = activity.return_current_duration()

        total_time += duration_to_add
        activity_durations[activity.name] += duration_to_add

        for tag in activity.tags:
            tag_durations[tag] += duration_to_add

    print('Activities Tracked: {} | Total Time Tracked: {}'.format(
        len(Activity.instances), str_format_timedelta(total_time)
    ))
    print()

    sort = sorted(activity_durations.items(), key=lambda x: x[1], reverse=True)
    for activity, duration in sort:
        print("{:<20} {:<15} {}".format(
            activity, str_format_timedelta(duration),
            percentage_of_timedelta(total_time, duration)
        ))

    print('', end='\n\n')

    print("Tags Tracked:", end='\n\n')

    sort = sorted(tag_durations.items(), key=lambda x: x[1], reverse=True)
    for tag, duration in sort:
        print("{:<20} {:<15} {}".format(
            tag, str_format_timedelta(duration),
            percentage_of_timedelta(total_time, duration)
        ))


def percentage_of_timedelta(total, duration):
    """Return percentage duration timedelta is of total timedelta."""
    proportion = duration.total_seconds() / total.total_seconds()
    return '{:.2%}'.format(proportion)


def edit_activity(activity_to_edit, info_to_edit, new_value):
    """Edit Activity information.

    Args:
        activity_to_edit (class member): The Activity to edit
        info_to_edit (str): String representing which variable to edit
        new_value (list): List containing the new value(s) for the variable

    """
    if info_to_edit.lower() in ('name', 'n'):
        activity_to_edit.name = new_value[0].title()

    elif info_to_edit.lower() in ('tag', 't'):
        activity_to_edit.tags = new_value

    elif info_to_edit.lower() in ('end', 'e'):
        activity_to_edit.update_datetime('end', new_value[0])

    elif info_to_edit.lower() in ('start', 's'):
        activity_to_edit.update_datetime('start', new_value[0])


def main():
    """Coordinate creation and time tracking of activities."""
    args = parse_arguments(sys.argv[1:])

    print()

    if args['begin']:
        if Activity.instances and not Activity.instances[-1].end:
            Activity.instances[-1].end_activity()
        Activity(' '.join(args['begin']))
        print(Activity.instances[-1])

    elif args['list']:
        print_list(calculate_date_range_start(args['list']))

    elif args['summary']:
        print_summary(calculate_date_range_start(args['summary']))

    # Args below IndexError if there are no Activity instances so catch here
    try:
        Activity.instances[-1]
    except IndexError:
        print(" No activities have been tracked")
        return

    if args['tag']:
        Activity.instances[-1].tags.extend(
            [tag.title() for tag in args['tag']]
        )

    elif args['current']:
        if Activity.instances[-1].end:
            print("Currently Not Tracking an Activity")
        else:
            print(Activity.instances[-1])

    elif args['finish']:
        Activity.instances[-1].end_activity()

    elif args['edit']:
        activity_to_edit = Activity.instances[int(args['edit'][0])]
        info_to_edit = args['edit'][1]
        new_value = args['edit'][2:]
        edit_activity(activity_to_edit, info_to_edit, new_value)

    print()
    return


if __name__ == '__main__':
    # Load data from data.pickle or create it if missing
    try:
        Activity.instances = unpickle_activities()
    except FileNotFoundError:
        with open('data.pickle', 'w') as file_creator:
            pass

    main()
    pickle_activities()
