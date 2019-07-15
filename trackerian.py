#!/usr/bin/env/ python3

"""Trackerian - a command line time tracker."""

import argparse
import datetime
import sys

def parse_arguments(args):
    """."""
    parser = argparse.ArgumentParser(description="Commandline Time Tracker")
    parser.add_argument('-b', '--begin', help='starts timing a task')


    if not args:
        parser.print_help()
        sys.exit


    return vars(parser.parse_args(args))


def begin_activity(activity_name, filestream):
    """Write activity name and current date to external file."""
    date_and_time = get_current_time_and_format()
    filestream.write('{} | {}\n'.format(activity_name, date_and_time))


def get_current_time_and_format():
    """Return current date and time as a formatted string."""
    date_format = '%Y-%m-%d %H:%M:%S'
    return datetime.datetime.now().strftime(date_format)






def main():
    """."""
    args = parse_arguments(sys.argv[1:])
    if args['begin']:
        with open('activity_log.txt', 'a') as filestream:
            begin_activity(args['begin'], filestream)


if __name__ == '__main__':
    main()
