#!/usr/bin/env python3

""" User Story Unit Testing for  Trackerian - a commandline time tracker."""

import datetime
import io
import sys
import unittest
import unittest.mock
from unittest.mock import patch

import trackerian


class TestParseArguments(unittest.TestCase):
    """Tests for trackerians parse_arguments() function."""

    # User runs trackerian.py from commandline and receives help instructions
    def test_no_arguments_prints_help(self):
        captured_output = capture_sys_stdout_in_string_io()
        trackerian.parse_arguments([])
        self.assertIn("usage:", captured_output.getvalue())

    # From help finds that --begin TASKNAME is how to start timing a task
    def test_begin_argument_stores_activity_name_in_returned_dict(self):
        args = trackerian.parse_arguments(['--begin', 'Activity Name'])
        self.assertEqual(args['begin'], 'Activity Name')

    # After some time finishes the task with the finish argument
    def test_finish_argument_stores_true_boolean_in_returned_dict(self):
        args = trackerian.parse_arguments(['--finish'])
        self.assertTrue(args['finish'])


class TestMain(unittest.TestCase):
    """Tests for trackerian's main()."""

    def tearDown(self):
        """Restore trackerian's Activity instances to a blank list."""
        trackerian.Activity.instances = []

    # Starts activity 'Activity' through --begin argument
    @patch('trackerian.parse_arguments')
    def test_begin_instantiates_activity_with_arg_name(self, mocked_args):
        mocked_args.return_value = edit_args_dict('begin', 'Activity')
        trackerian.main()
        self.assertEqual(trackerian.Activity.instances[0].name, 'Activity')

    @patch('trackerian.parse_arguments')
    def test_begin_prints_confirmation_of_task_start(self, mocked_args):
        mocked_args.return_value = edit_args_dict('begin', 'Activity Printed')
        captured_output = capture_sys_stdout_in_string_io()
        trackerian.main()
        self.assertIn('Activity Printed', captured_output.getvalue())

    # Ends activity through --finish
    @patch('trackerian.parse_arguments')
    def test_finish_adds_end_variable_to_last_instance(self, mocked_args):
        trackerian.Activity('To End')
        mocked_args.return_value = edit_args_dict('finish', True)
        trackerian.main()
        self.assertTrue(trackerian.Activity.instances[0].end)


class TestEndActivityActivityClassMethod(unittest.TestCase):
    """Tests for end_activity method of Activity class."""

    def setUp(self):
        """Create instance and set start to known datetime object."""
        trackerian.Activity('End Activity Tests')
        controlled_start_datetime = datetime.datetime(2010, 10, 10, 10, 10, 00)
        trackerian.Activity.instances[0].start = controlled_start_datetime

    def tearDown(self):
        """Restore trackerian's Activity instances to a blank list."""
        trackerian.Activity.instances = []

    @patch('trackerian.get_current_time')
    def test_end_variable_set_to_correct_datetime(self, mocked_time):
        end_datetime_object = datetime.datetime(2010, 10, 10, 10, 20, 00)
        mocked_time.return_value = end_datetime_object
        trackerian.Activity.instances[0].end_activity()
        end = trackerian.Activity.instances[0].end
        self.assertEqual(end, end_datetime_object)

    @patch('trackerian.get_current_time')
    def test_duration_set_to_correct_timedelta(self, mocked_time):
        mocked_time.return_value = datetime.datetime(2010, 10, 10, 10, 40, 00)
        trackerian.Activity.instances[0].end_activity()
        duration = trackerian.Activity.instances[0].duration
        self.assertEqual(duration, datetime.timedelta(0, 1800))

    @patch('trackerian.get_current_time')
    def test_confirmation_of_activity_duration_printed(self, mocked_time):
        mocked_time.return_value = datetime.datetime(2010, 10, 10, 11, 40, 00)
        captured_output = capture_sys_stdout_in_string_io()
        trackerian.Activity.instances[0].end_activity()
        self.assertIn('1:30:00', captured_output.getvalue())


def capture_sys_stdout_in_string_io():
    """Capture the systems standard output - facilitates assertion tests."""
    sys.stdout = io.StringIO()
    return sys.stdout


def edit_args_dict(key, new_value):
    """Edit defaulted argument dictionary and return it.

    Args:
        key (str): Key of the dictionary to change from default.
        new_value (str, boolean): New value to set key dictionary entry to.

    Returns:
        Args dictionary with argument specified modification applied

    """
    defaulted_args_dict = {
        'begin': None,
        'finish': False,
    }
    defaulted_args_dict[key] = new_value
    return defaulted_args_dict


if __name__ == '__main__':
    unittest.main()
