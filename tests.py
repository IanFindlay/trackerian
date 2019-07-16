#!/usr/bin/env python3

""" User Story Testing for  Trackerian - a commandline time tracker."""

import datetime
import io
import sys
import unittest
import unittest.mock
from unittest.mock import patch

import trackerian


class TestParseArguments(unittest.TestCase):
    """Tests for trackerians parse_arguments()."""

    # User runs trackerian.py from commandline and receives help instructions
    def test_no_argument_prints_help(self):
        """Invoking the program with no arguments prints help."""
        captured_output = io.StringIO()
        sys.stdout = captured_output
        trackerian.parse_arguments([])

        self.assertIn("usage:", captured_output.getvalue())

    # From help finds that --begin TASKNAME is how to start timing a task
    def test_begin_argument_stores_activity_name_in_return(self):
        """--begin stores argument in args dictionary."""
        args = trackerian.parse_arguments(['--begin', 'Activity Name'])

        self.assertEqual(args['begin'], 'Activity Name')

    # After some time finishes the task with the finish argument
    def test_finish_argument_stores_true_in_end_return(self):
        """--finish stores True boolean in args dictionary."""
        args = trackerian.parse_arguments(['--finish'])

        self.assertTrue(args['finish'])


class TestMain(unittest.TestCase):
    """Tests for trackerian's main()."""

    def setUp(self):
        trackerian.Activity.instances = []

    # Starts activity 'Activity' through --begin argument
    @patch('trackerian.parse_arguments')
    def test_begin_instantiates_activity_with_arg_name(self, mocked_args):
        """New member of Activity class with argument name instantiated."""
        mocked_args.return_value = {'begin': 'Activity', 'finish': True}
        trackerian.main()

        self.assertEqual(trackerian.Activity.instances[0].name, 'Activity')

    # Ends activity through --finish
    @patch('trackerian.parse_arguments')
    def test_finish_adds_end_to_previous_instance(self, mocked_args):
        """."""
        trackerian.Activity('To be ended')
        mocked_args.return_value = {'begin': None, 'finish': True}
        trackerian.main()

        self.assertTrue(trackerian.Activity.instances[0].endtime)


class TestEndActivityActivityClassMethod(unittest.TestCase):
    """."""

    def test_endtime_variable_set_to_datetime(self):
        """."""
        trackerian.Activity('End Me')
        trackerian.Activity.instances[0].end_activity()
        endtime = trackerian.Activity.instances[0].endtime

        self.assertTrue(isinstance(endtime, datetime.date))

    @patch('trackerian.get_current_time')
    def test_duration_set_to_correct_time(self, mocked_time):
        """Use str representation of timedelta object to check duration."""
        mocked_time.side_effect = [datetime.datetime(2010, 10, 10, 10, 10, 10),
                                   datetime.datetime(2010, 10, 10, 10, 40, 00)]
        trackerian.Activity('Duration Check')
        trackerian.Activity.instances[0].end_activity()
        duration = trackerian.Activity.instances[0].duration

        self.assertEqual(str(duration), '0:29:50')


if __name__ == '__main__':
    unittest.main()
