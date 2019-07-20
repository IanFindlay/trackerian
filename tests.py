#!/usr/bin/env python3

""" User Story Unit Testing for  Trackerian - a commandline time tracker."""

import collections
import datetime
import io
import unittest
import unittest.mock
from unittest.mock import patch

import trackerian


class TestParseArguments(unittest.TestCase):
    """Tests for trackerians parse_arguments() function."""

    # User runs trackerian.py from command line and receives help instructions
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_no_arguments_prints_help(self, mocked_stdout):
        trackerian.parse_arguments([])
        self.assertIn("usage:", mocked_stdout.getvalue())

    # From help finds that --begin TASKNAME is how to start timing a task
    def test_begin_argument_stores_activity_name_in_returned_dict(self):
        args = trackerian.parse_arguments(['--begin', 'Activity Name'])
        self.assertEqual(args['begin'], 'Activity Name')

    # After some time finishes the task with the --finish argument
    def test_finish_argument_stores_true_boolean_in_returned_dict(self):
        args = trackerian.parse_arguments(['--finish'])
        self.assertEqual(args['finish'], True)

    # User passes --current argument to check if an activity is being tracked
    def test_current_argument_stores_true_boolean_in_returned_dict(self):
        args = trackerian.parse_arguments(['--current'])
        self.assertEqual(args['current'], True)

    # User passes --summary to see information about past/current activities
    def test_summary_argument_stores_true_boolean_in_returned_dict(self):
        args = trackerian.parse_arguments(['--summary'])
        self.assertEqual(args['summary'], True)


class TestMainBegin(unittest.TestCase):
    """Tests for how main() deals with the begin arg."""

    def tearDown(self):
        """Restore trackerian's Activity instances to a empty list."""
        trackerian.Activity.instances = []

    # Starts activity 'Activity' through --begin argument
    @patch('trackerian.parse_arguments')
    def test_begin_instantiates_activity_with_arg_name(self, mocked_args):
        mocked_args.return_value = edit_args_dict('begin', 'Activity')
        trackerian.main()
        self.assertEqual(trackerian.Activity.instances[0].name, 'Activity')

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('trackerian.parse_arguments')
    def test_begin_prints__about_task_start(self, mocked_args, mocked_stdout):
        mocked_args.return_value = edit_args_dict('begin', 'Activity Printed')
        trackerian.main()
        self.assertIn('Activity Printed', mocked_stdout.getvalue())

    @patch('trackerian.parse_arguments')
    def test_begin_ends_previous_process_if_not_ended(self, mocked_args):
        trackerian.Activity('Begin Should End This')
        mocked_args.return_value = edit_args_dict('begin', 'New Actvity')
        trackerian.main()
        self.assertTrue(trackerian.Activity.instances[0].end)


class TestMainFinish(unittest.TestCase):
    """Tests for how main() deals with the finish arg."""

    def tearDown(self):
        """Restore trackerian's Activity instances to a empty list."""
        trackerian.Activity.instances = []

    # Ends activity through --finish
    @patch('trackerian.parse_arguments')
    def test_finish_adds_end_to_last_instance_if_not_ended(self, mocked_args):
        trackerian.Activity('To End')
        mocked_args.return_value = edit_args_dict('finish', True)
        trackerian.main()
        self.assertTrue(trackerian.Activity.instances[-1].end)

    @patch('trackerian.parse_arguments')
    def test_finish_raises_index_error_when_no_instances(self, mocked_args):
        mocked_args.return_value = edit_args_dict('finish', True)
        self.assertRaises(IndexError, trackerian.main())


class TestMainCurrent(unittest.TestCase):
    """Tests for how main() deals with the current arg."""

    def tearDown(self):
        """Restore trackerian's Activity instances to a empty list."""
        trackerian.Activity.instances = []

    # Checks on current activity using --current and info is printed
    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('trackerian.parse_arguments')
    def test_current_prints_activity_name_if_not_ended(self, mocked_args,
                                                       mocked_stdout):
        trackerian.Activity('Current Activity')
        mocked_args.return_value = edit_args_dict('current', True)
        trackerian.main()
        self.assertIn('Current Activity', mocked_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('trackerian.parse_arguments')
    def test_current_prints_current_duration_if_not_ended(self, mocked_args,
                                                          mocked_stdout):
        trackerian.Activity('Current Activity')
        mocked_args.return_value = edit_args_dict('current', True)
        trackerian.main()
        self.assertIn('0:00:', mocked_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('trackerian.parse_arguments')
    def test_current_prints_message_if_no_activity_running(self, mocked_args,
                                                           mocked_stdout):
        trackerian.Activity('Ended Activity')
        trackerian.Activity.instances[-1].end = True
        mocked_args.return_value = edit_args_dict('current', True)
        trackerian.main()
        self.assertIn('Not Tracking', mocked_stdout.getvalue())

    @patch('trackerian.parse_arguments')
    def test_current_raises_index_error_when_no_instances(self, mocked_args):
        mocked_args.return_value = edit_args_dict('current', True)
        self.assertRaises(IndexError, trackerian.main())


class TestMainList(unittest.TestCase):
    """Tests for how main() deals with the list arg."""

    def setUp(self):
        """Create two instances of Activity class one of which has ended."""
        trackerian.Activity('First Activity')
        trackerian.Activity.instances[0].end_activity()
        trackerian.Activity('Second Activity')

    def tearDown(self):
        """Restore trackerian's Activity instances to empty list."""
        trackerian.Activity.instances = []

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('trackerian.parse_arguments')
    def test_prints_name_of_first_activity(self, mocked_args, mocked_stdout):
        mocked_args.return_value = edit_args_dict('list', True)
        trackerian.main()
        self.assertIn('First Activity', mocked_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('trackerian.parse_arguments')
    def test_prints_name_of_second_activity(self, mocked_args, mocked_stdout):
        mocked_args.return_value = edit_args_dict('list', True)
        trackerian.main()
        self.assertIn('Second Activity', mocked_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('trackerian.parse_arguments')
    def test_prints_duration_of_finished(self, mocked_args, mocked_stdout):
        mocked_args.return_value = edit_args_dict('list', True)
        trackerian.main()
        self.assertIn(
            str(trackerian.Activity.instances[0].duration).split('.')[0],
            mocked_stdout.getvalue()
        )


class TestPrintSummary(unittest.TestCase):
    """Tests for print_summary function."""

    def setUp(self):
        """Create two instances of Activity class one ended after 30 mins."""
        trackerian.Activity('30Minutes')
        trackerian.Activity.instances[0].end_activity()
        trackerian.Activity.instances[0].duration = datetime.timedelta(0, 1800)
        trackerian.Activity('15Minutes')

    def tearDown(self):
        """Restore trackerian's Activity instances to empty list."""
        trackerian.Activity.instances = []

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_prints_number_of_tracked(self, mocked_stdout):
        trackerian.print_summary()
        self.assertIn('Activities Tracked: 2', mocked_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('trackerian.Activity.return_current_duration')
    def test_prints_total_time_tracked(self, mocked_duration, mocked_stdout):
        mocked_duration.return_value = datetime.timedelta(0, 900)
        trackerian.print_summary()
        self.assertIn('0:45:00', mocked_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_activities_grouped_by_name(self, mocked_stdout):
        trackerian.Activity('30Minutes')
        trackerian.print_summary()
        word_count = collections.Counter(mocked_stdout.getvalue().split())
        self.assertTrue(word_count['30Minutes'] == 1)

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('trackerian.Activity.return_current_duration')
    def test_grouped_activities_duration(self, mocked_duration, mocked_stdout):
        mocked_duration.return_value = datetime.timedelta(0, 300)
        trackerian.Activity('30Minutes')
        trackerian.print_summary()
        self.assertIn('0:35:00', mocked_stdout.getvalue())


class TestEndActivityActivityClassMethod(unittest.TestCase):
    """Tests for end_activity method of Activity class."""

    def setUp(self):
        """Create instance and set start to known datetime object."""
        trackerian.Activity('End Activity Tests')
        controlled_start_datetime = datetime.datetime(2010, 10, 10, 10, 10, 00)
        trackerian.Activity.instances[0].start = controlled_start_datetime

    def tearDown(self):
        """Restore trackerian's Activity instances to a empty list."""
        trackerian.Activity.instances = []

    @patch('trackerian.get_current_time')
    def test_end_variable_set_to_correct_datetime(self, mocked_time):
        end_datetime_object = datetime.datetime(2010, 10, 10, 10, 20, 00)
        mocked_time.return_value = end_datetime_object
        trackerian.Activity.instances[0].end_activity()
        end = trackerian.Activity.instances[0].end
        self.assertEqual(end, end_datetime_object)

    @patch('trackerian.get_current_time')
    def test_end_str_variable_set_correctly(self, mocked_time):
        end_datetime_object = datetime.datetime(2010, 10, 10, 10, 30, 00)
        mocked_time.return_value = end_datetime_object
        trackerian.Activity.instances[0].end_activity()
        end_str = trackerian.Activity.instances[0].end_str
        self.assertEqual(end_str, '10:30:00')

    @patch('trackerian.get_current_time')
    def test_duration_set_to_correct_timedelta(self, mocked_time):
        mocked_time.return_value = datetime.datetime(2010, 10, 10, 10, 40, 00)
        trackerian.Activity.instances[0].end_activity()
        duration = trackerian.Activity.instances[0].duration
        self.assertEqual(duration, datetime.timedelta(0, 1800))

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('trackerian.get_current_time')
    def test_activity_duration_printed(self, mocked_time, mocked_stdout):
        mocked_time.return_value = datetime.datetime(2010, 10, 10, 11, 40, 00)
        trackerian.Activity.instances[0].end_activity()
        self.assertIn('1:30:00', mocked_stdout.getvalue())

    def test_does_not_modify_end_if_already_set(self):
        trackerian.Activity.instances[0].end_activity()
        initial_end = trackerian.Activity.instances[0].end
        trackerian.Activity.instances[0].end_activity()
        self.assertEqual(trackerian.Activity.instances[0].end, initial_end)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_prints_message_if_activity_already_ended(self, mocked_stdout):
        trackerian.Activity.instances[0].end_activity()
        trackerian.Activity.instances[0].end_activity()
        self.assertIn('already finished', mocked_stdout.getvalue())


class TestReturnCurrentDurationActivityClassMethod(unittest.TestCase):
    """Tests for return_current_duration method of Activity class."""

    def tearDown(self):
        """Restore trackerian's Activity instances to a empty list."""
        trackerian.Activity.instances = []

    @patch('trackerian.get_current_time')
    def test_returns_accurate_timedelta_object(self, mocked_time):
        mocked_time.side_effect = [
            datetime.datetime(2012, 12, 12, 12, 30, 00),
            datetime.datetime(2012, 12, 12, 13, 00, 00)
        ]
        trackerian.Activity('Check Duration')
        duration = trackerian.Activity.instances[-1].return_current_duration()
        self.assertEqual(duration, datetime.timedelta(0, 1800))


class TestStrFormatDatetime(unittest.TestCase):
    """Tests for str_format_datetime function."""

    def test_returns_str(self):
        test_date = datetime.datetime(2014, 4, 4, 4, 40, 00)
        self.assertTrue(
            isinstance(trackerian.str_format_datetime(test_date), str)
        )


class TestStrFormatTimedelta(unittest.TestCase):
    """Test for str_format_timedelta function."""

    def test_return_str(self):
        test_delta = datetime.timedelta(0, 300)
        self.assertTrue(
            isinstance(trackerian.str_format_timedelta(test_delta), str)
        )

    def test_zero_pads_hour(self):
        test_delta = datetime.timedelta(0, 300)
        self.assertEqual(
            trackerian.str_format_timedelta(test_delta), '00:05:00'
        )

    def test_return_has_milliseconds_trimmed(self):
        test_delta = datetime.timedelta(0, 600, 250)
        self.assertEqual(
            trackerian.str_format_timedelta(test_delta), '00:10:00'
        )


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
        'current': False,
        'summary': False,
        'list': False,
    }
    defaulted_args_dict[key] = new_value
    return defaulted_args_dict


if __name__ == '__main__':
    unittest.main()
