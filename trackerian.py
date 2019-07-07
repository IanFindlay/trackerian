#!/usr/bin/env/ python3

"""Trackerian - a command line time tracker."""

import argparse
import sys

def parse_arguments():
    """."""
    parser = argparse.ArgumentParser(description="Commandline Time Tracker")


    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit


    return vars(parser.parse_args())





parse_arguments()
