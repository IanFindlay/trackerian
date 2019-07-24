#!/usr/bin/env python3

""" Unit Tests for  Trackerian - a command line time tracker."""

import collections
import datetime
import io
import unittest
import unittest.mock
from unittest.mock import patch

import trackerian


class TestParseArguments(unittest.TestCase):
    """Tests for trackerians parse_arguments() function."""

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_no_arguments_prints_help(self, mocked_stdout):
        trackerian.parse_arguments([])
        self.assertIn("usage:", mocked_stdout.getvalue())

    def test_begin_stores_activity_name_in_returned_dict(self):
        args = trackerian.parse_arguments(['--begin', 'Activity Name'])
        self.assertEqual(args['begin'], 'Activity Name')

    def test_finish_stores_true_boolean_in_returned_dict(self):
        args = trackerian.parse_arguments(['--finish'])
        self.assertEqual(args['finish'], True)

    def test_current_stores_true_boolean_in_returned_dict(self):
        args = trackerian.parse_arguments(['--current'])
        self.assertEqual(args['current'], True)

    def test_summary_defaults_to_day(self):
        args = trackerian.parse_arguments(['--summary'])
        self.assertEqual(args['summary'], 'day')

    def test_summary_stores_valid_choice_in_returned_dict(self):
        args = trackerian.parse_arguments(['--summary', 'all'])
        self.assertEqual(args['summary'], 'all')

    @patch('sys.stderr', new_callable=io.StringIO)
    def test_summary_invalid_choice_in_error(self, mocked_stderr):
        try:
            trackerian.parse_arguments(['--summary', 'invalid'])
        except:
            pass
        self.assertIn('invalid choice:', mocked_stderr.getvalue())

    def test_list_stores_true_boolean_in_returned_dict(self):
        args = trackerian.parse_arguments(['--list'])
        self.assertEqual(args['list'], True)

    def test_tag_stores_tag_string_in_returned_dict(self):
        args = trackerian.parse_arguments(['--tag', 'Testing Tag'])
        self.assertEqual(args['tag'], 'Testing Tag')


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


class TestMainTag(unittest.TestCase):
    """Tests for how main() deals with the tag arg."""

    def setUp(self):
        """Instantiate an Activity."""
        trackerian.Activity('Running')

    def tearDown(self):
        """Restore trackerian's Activity instances to empty list."""
        trackerian.Activity.instances = []

    @patch('trackerian.parse_arguments')
    def test_adds_tag_to_running_activity(self, mocked_args):
        mocked_args.return_value = edit_args_dict('tag', 'tagged')
        trackerian.main()
        self.assertEqual(
            trackerian.Activity.instances[0].tags, ['tagged']
        )

    @patch('trackerian.parse_arguments')
    def test_adds_multiple_tags_to_running_activity(self, mocked_args):
        mocked_args.return_value = edit_args_dict('tag', 'tagged twice')
        trackerian.main()
        self.assertEqual(
            trackerian.Activity.instances[0].tags, ['tagged', 'twice']
        )

    @patch('trackerian.parse_arguments')
    def test_adds_tag_to_latest_finished_activity(self, mocked_args):
        mocked_args.return_value = edit_args_dict('tag', 'tagged')
        trackerian.Activity.instances[0].end = 'Ended'
        trackerian.main()
        self.assertEqual(
            trackerian.Activity.instances[0].tags, ['tagged']
        )

    @patch('trackerian.parse_arguments')
    def test_adds_multiple_tags_to_latest_finished_activity(self, mocked_args):
        mocked_args.return_value = edit_args_dict('tag', 'tagged twice')
        trackerian.Activity.instances[0].end = 'Ended'
        trackerian.main()
        self.assertEqual(
            trackerian.Activity.instances[0].tags, ['tagged', 'twice']
        )

    @patch('trackerian.parse_arguments')
    def test_tags_are_added_as_lowercase_to_instance(self, mocked_args):
        mocked_args.return_value = edit_args_dict('tag', 'Title UPPERCASE')
        trackerian.main()
        self.assertEqual(
            trackerian.Activity.instances[0].tags, ['title', 'uppercase']
        )


class TestMainSummary(unittest.TestCase):
    """Tests for how main() deals with summary args."""

    @patch('trackerian.print_summary')
    @patch('trackerian.parse_arguments')
    def test_day_passes_today_datetime_to_print_summary(self, mocked_args,
                                                        mocked_summary):
        mocked_args.return_value = edit_args_dict('summary', 'day')
        trackerian.main()
        passed_datetime = mocked_summary.call_args[0][0]
        datetime_difference = passed_datetime - datetime.datetime.now()
        self.assertTrue(datetime_difference <= datetime.timedelta(hours=24))

    @patch('trackerian.print_summary')
    @patch('trackerian.parse_arguments')
    def test_no_arg_passed_to_print_summary_with_all_arg(self, mocked_args,
                                                         mocked_summary):
        mocked_args.return_value = edit_args_dict('summary', 'all')
        trackerian.main()
        self.assertEqual(mocked_summary.call_args[0], ())


class TestPrintSummary(unittest.TestCase):
    """Tests for print_summary function."""

    def setUp(self):
        """Create three instances of Activity class.

        First has two tags and a duration of 30 minutes.
        Second has same name and duration as first but only one tag in common.
        Third is ongoing and shares a tag with the first but not the second.

        """
        trackerian.Activity('30Minutes')
        trackerian.Activity.instances[0].tags = ['TagOne', 'TagTwo']
        trackerian.Activity.instances[0].end_activity()
        trackerian.Activity.instances[0].duration = datetime.timedelta(0, 1800)

        trackerian.Activity('30Minutes')
        trackerian.Activity.instances[1].tags = ['TagOne']
        trackerian.Activity.instances[1].end_activity()
        trackerian.Activity.instances[1].duration = datetime.timedelta(0, 1800)

        trackerian.Activity('Variable')
        trackerian.Activity.instances[-1].tags = ['TagOne', 'TagTwo']

    def tearDown(self):
        """Restore trackerian's Activity instances to empty list."""
        trackerian.Activity.instances = []

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_prints_number_of_tracked(self, mocked_stdout):
        trackerian.print_summary()
        self.assertIn('Activities Tracked: 3', mocked_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('trackerian.Activity.return_current_duration')
    def test_prints_total_time(self, mocked_duration, mocked_stdout):
        mocked_duration.return_value = datetime.timedelta(0, 900)
        trackerian.print_summary()
        self.assertIn('01:15:00', mocked_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_activities_grouped_by_name(self, mocked_stdout):
        trackerian.Activity('30Minutes')
        trackerian.print_summary()
        word_count = collections.Counter(mocked_stdout.getvalue().split())
        self.assertTrue(word_count['30Minutes'] == 1)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_name_grouping_case_insensitive(self, mocked_stdout):
        trackerian.Activity('30MINUTES')
        trackerian.print_summary()
        word_count = collections.Counter(mocked_stdout.getvalue().split())
        self.assertTrue(word_count['30MINUTES'] == 0)

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('trackerian.Activity.return_current_duration')
    def test_name_grouped_duration_shown(self, mocked_duration, mocked_stdout):
        mocked_duration.return_value = datetime.timedelta(0, 60)
        trackerian.print_summary()
        # Activity 3 given 1 min current duration so total isn't same as name
        self.assertIn('01:00:00', mocked_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_tags_printed(self, mocked_stdout):
        trackerian.print_summary()
        self.assertIn('TagOne', mocked_stdout.getvalue())
        self.assertIn('TagTwo', mocked_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('trackerian.Activity.return_current_duration')
    def test_tag_grouped_duration(self, mocked_duration, mocked_stdout):
        mocked_duration.return_value = datetime.timedelta(0, 600)
        trackerian.print_summary()
        # Activity 3 given 10 minutes current duration so tag one = 01:10:00
        self.assertIn('01:10:00', mocked_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_earlier_than_range_start_datetime_ignored(self, mocked_stdout):
        date_range_start = datetime.datetime.now()
        trackerian.Activity('Alone')
        trackerian.print_summary(date_range_start)
        self.assertNotIn('30Minutes', mocked_stdout.getvalue())


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
        'tag': None,
    }
    defaulted_args_dict[key] = new_value
    return defaulted_args_dict


if __name__ == '__main__':
    unittest.main()
