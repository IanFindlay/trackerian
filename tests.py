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

    def test_begin_stores_activity_name_words_in_returned_dict(self):
        args = trackerian.parse_arguments(['--begin', 'Activity', 'Name'])
        self.assertEqual(args['begin'], ['Activity', 'Name'])

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

    def test_tag_stores_tag_list_in_returned_dict(self):
        args = trackerian.parse_arguments(['--tag', 'Args', 'Listed'])
        self.assertEqual(args['tag'], ['Args', 'Listed'])


class TestMainBegin(unittest.TestCase):
    """Tests for how main() deals with the begin arg."""

    def tearDown(self):
        """Restore trackerian's Activity instances to a empty list."""
        trackerian.Activity.instances = []

    @patch('trackerian.parse_arguments')
    def test_instantiates_activity_with_arg_name(self, mocked_args):
        mocked_args.return_value = edit_args_dict('begin', ['Activity'])
        trackerian.main()
        self.assertEqual(trackerian.Activity.instances[0].name, 'Activity')

    @patch('trackerian.parse_arguments')
    def test_instantiates_activity_with_joined_arg_name(self, mocked_args):
        mocked_args.return_value = edit_args_dict('begin', ['Split', 'Name'])
        trackerian.main()
        self.assertEqual(trackerian.Activity.instances[0].name, 'Split Name')

    @patch('trackerian.get_current_datetime')
    @patch('trackerian.parse_arguments')
    def test_instantiates_activity_with_formatted_start_str(self, mocked_args,
                                                            mocked_time):
        mocked_args.return_value = edit_args_dict('begin', ['String'])
        mocked_time.return_value = datetime.datetime(2018, 11, 12, 21, 22, 23)
        trackerian.main()
        instance_start_str = trackerian.Activity.instances[0].start_str
        self.assertEqual(instance_start_str, '21:22:23')

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('trackerian.parse_arguments')
    def test_prints_about_task_start(self, mocked_args, mocked_stdout):
        mocked_args.return_value = edit_args_dict('begin', ['Print', 'Test'])
        trackerian.main()
        self.assertIn('Print Test', mocked_stdout.getvalue())

    @patch('trackerian.parse_arguments')
    def test_ends_previous_process_if_not_ended(self, mocked_args):
        trackerian.Activity('Begin Should End This')
        mocked_args.return_value = edit_args_dict('begin', ['New', 'Actvity'])
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
        trackerian.Activity('Finished Activity')
        trackerian.Activity.instances[0].end_activity()
        trackerian.Activity('Running Activity')

    def tearDown(self):
        """Restore trackerian's Activity instances to an empty list."""
        trackerian.Activity.instances = []

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('trackerian.parse_arguments')
    def test_prints_finished_activity_name(self, mocked_args, mocked_stdout):
        mocked_args.return_value = edit_args_dict('list', True)
        trackerian.main()
        self.assertIn('Finished Activity', mocked_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('trackerian.parse_arguments')
    def test_running_activity_name(self, mocked_args, mocked_stdout):
        mocked_args.return_value = edit_args_dict('list', True)
        trackerian.main()
        self.assertIn('Running Activity', mocked_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('trackerian.parse_arguments')
    def test_prints_duration_of_finished(self, mocked_args, mocked_stdout):
        mocked_args.return_value = edit_args_dict('list', True)
        trackerian.main()
        self.assertIn(
            str(trackerian.Activity.instances[0].duration).split('.')[0],
            mocked_stdout.getvalue()
        )

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('trackerian.parse_arguments')
    def test_prints_tags_on_finished(self, mocked_args, mocked_stdout):
        mocked_args.return_value = edit_args_dict('list', True)
        trackerian.Activity.instances[0].tags = ['Tags']
        trackerian.main()
        self.assertIn('Tags', mocked_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('trackerian.parse_arguments')
    def test_prints_tags_on_running(self, mocked_args, mocked_stdout):
        mocked_args.return_value = edit_args_dict('list', True)
        trackerian.Activity.instances[-1].tags = ['Testing']
        trackerian.main()
        self.assertIn('Testing', mocked_stdout.getvalue())


class TestMainTag(unittest.TestCase):
    """Tests for how main() deals with the tag arg."""

    def setUp(self):
        """Instantiate an Activity."""
        trackerian.Activity('Running')

    def tearDown(self):
        """Restore trackerian's Activity instances to an empty list."""
        trackerian.Activity.instances = []

    @patch('trackerian.parse_arguments')
    def test_adds_tag_to_running_activity(self, mocked_args):
        mocked_args.return_value = edit_args_dict('tag', ['tagged'])
        trackerian.main()
        self.assertEqual(
            trackerian.Activity.instances[0].tags, ['Tagged']
        )

    @patch('trackerian.parse_arguments')
    def test_adds_multiple_tags_to_running_activity(self, mocked_args):
        mocked_args.return_value = edit_args_dict('tag', ['tagged', 'twice'])
        trackerian.main()
        self.assertEqual(
            trackerian.Activity.instances[0].tags, ['Tagged', 'Twice']
        )

    @patch('trackerian.parse_arguments')
    def test_adds_tag_to_latest_finished_activity(self, mocked_args):
        mocked_args.return_value = edit_args_dict('tag', ['tagged'])
        trackerian.Activity.instances[0].end = 'Ended'
        trackerian.main()
        self.assertEqual(
            trackerian.Activity.instances[0].tags, ['Tagged']
        )

    @patch('trackerian.parse_arguments')
    def test_adds_multiple_tags_to_latest_finished_activity(self, mocked_args):
        mocked_args.return_value = edit_args_dict('tag', ['tagged', 'twice'])
        trackerian.Activity.instances[0].end = 'Ended'
        trackerian.main()
        self.assertEqual(
            trackerian.Activity.instances[0].tags, ['Tagged', 'Twice']
        )

    @patch('trackerian.parse_arguments')
    def test_tags_are_added_as_title_case_to_instance(self, mocked_args):
        mocked_args.return_value = edit_args_dict('tag', ['Title', 'UPPER'])
        trackerian.main()
        self.assertEqual(
            trackerian.Activity.instances[0].tags, ['Title', 'Upper']
        )


class TestMainEdit(unittest.TestCase):
    """Tests for how main() deals with edit args."""

    def setUp(self):
        """Instantiate two different activities"""
        trackerian.Activity('Activity Zero')
        trackerian.Activity('Activity One')

    def tearDown(self):
        """Restore trackerian's Activity instances to an empty list."""
        trackerian.Activity.instances = []

    @patch('trackerian.edit_activity')
    @patch('trackerian.parse_arguments')
    def test_correct_activity_argument_passed(self, mocked_args, mocked_edit):
        mocked_args.return_value = edit_args_dict('edit', ['0', 'name', 'new'])
        trackerian.main()
        correct_activity = trackerian.Activity.instances[0]
        self.assertEqual(mocked_edit.call_args[0][0], correct_activity)

    @patch('trackerian.edit_activity')
    @patch('trackerian.parse_arguments')
    def test_correct_info_argument_passed(self, mocked_args, mocked_edit):
        mocked_args.return_value = edit_args_dict('edit', ['1', 'tag', 'test'])
        trackerian.main()
        self.assertEqual(mocked_edit.call_args[0][1], 'tag')

    @patch('trackerian.edit_activity')
    @patch('trackerian.parse_arguments')
    def test_correct_new_value_argument_passed(self, mocked_args, mocked_edit):
        mocked_args.return_value = edit_args_dict(
            'edit', ['0', 'end', '11:22:44']
        )
        trackerian.main()
        self.assertEqual(mocked_edit.call_args[0][2], ['11:22:44'])


class TestMainSummary(unittest.TestCase):
    """Tests for how main() deals with summary args."""

    @patch('trackerian.calculate_summary_date_range_start')
    @patch('trackerian.parse_arguments')
    def test_day_passes_day_to_calculate_summary(self, mocked_args,
                                                 mocked_calculate):
        mocked_args.return_value = edit_args_dict('summary', 'day')
        trackerian.main()
        self.assertEqual(mocked_calculate.call_args[0][0], 'day')

    @patch('trackerian.calculate_summary_date_range_start')
    @patch('trackerian.parse_arguments')
    def test_week_passes_week_to_calculate_summary(self, mocked_args,
                                                  mocked_calculate):
        mocked_args.return_value = edit_args_dict('summary', 'week')
        trackerian.main()
        self.assertEqual(mocked_calculate.call_args[0][0], 'week')

    @patch('trackerian.calculate_summary_date_range_start')
    @patch('trackerian.parse_arguments')
    def test_all_passed_to_caclculate_summary_with_no_arg(self, mocked_args,
                                                          mocked_calculate):
        mocked_args.return_value = edit_args_dict('summary', 'all')
        trackerian.main()
        self.assertEqual(mocked_calculate.call_args[0][0], 'all')


class TestCalculateSummaryDateRangeStart(unittest.TestCase):
    """Tests for calculate_summary_date_range_start function."""

    def test_return_none_when_all_arg_passed(self):
        test_return = trackerian.calculate_summary_date_range_start('all')
        self.assertEqual(test_return, None)

    @patch('trackerian.get_current_datetime')
    def test_return_early_today_datetime_when_day_arg(self, mocked_date):
        mocked_date.return_value = datetime.datetime(2018, 12, 12, 12, 12, 12)
        test_return = trackerian.calculate_summary_date_range_start('day')
        eight_today = datetime.datetime(2018, 12, 12, 8, 0, 0)
        yesterday_night = datetime.datetime(2018, 12, 11, 23, 59)
        self.assertTrue(yesterday_night < test_return < eight_today)

    @patch('trackerian.get_current_datetime')
    def test_return_week_ago_datetime_when_week_arg(self, mocked_date):
        mocked_date.return_value = datetime.datetime(2017, 10, 14, 14, 14, 14)
        test_return = trackerian.calculate_summary_date_range_start('week')
        print(test_return)
        eight_days_ago = datetime.datetime(2017, 10, 6, 23, 59, 0)
        early_week_ago = datetime.datetime(2017, 10, 7, 8, 0)
        self.assertTrue(eight_days_ago < test_return < early_week_ago)


class TestPrintSummary(unittest.TestCase):
    """Tests for print_summary function."""

    def setUp(self):
        """Create three instances of Activity class.

        First has two tags and a duration of 30 minutes.
        Second has same name and duration as first but only one tag in common.
        Third is ongoing and shares a tag with the first but not the second.

        """
        half_hour = datetime.timedelta(minutes=30)
        trackerian.Activity('30Minutes')
        trackerian.Activity.instances[0].tags = ['TagOne', 'TagTwo']
        trackerian.Activity.instances[0].end_activity()
        trackerian.Activity.instances[0].duration = half_hour

        trackerian.Activity('30Minutes')
        trackerian.Activity.instances[1].tags = ['TagOne']
        trackerian.Activity.instances[1].end_activity()
        trackerian.Activity.instances[1].duration = half_hour

        trackerian.Activity('Variable')
        trackerian.Activity.instances[-1].tags = ['TagOne', 'TagTwo']

    def tearDown(self):
        """Restore trackerian's Activity instances to an empty list."""
        trackerian.Activity.instances = []

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_prints_number_of_tracked(self, mocked_stdout):
        trackerian.print_summary(None)
        self.assertIn('Activities Tracked: 3', mocked_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('trackerian.Activity.return_current_duration')
    def test_prints_total_time(self, mocked_duration, mocked_stdout):
        mocked_duration.return_value = datetime.timedelta(minutes=15)
        trackerian.print_summary(None)
        self.assertIn('01:15:00', mocked_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_activities_grouped_by_name(self, mocked_stdout):
        trackerian.Activity('30Minutes')
        trackerian.print_summary(None)
        word_count = collections.Counter(mocked_stdout.getvalue().split())
        self.assertTrue(word_count['30Minutes'] == 1)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_name_grouping_case_insensitive(self, mocked_stdout):
        trackerian.Activity('30MINUTES')
        trackerian.print_summary(None)
        word_count = collections.Counter(mocked_stdout.getvalue().split())
        self.assertTrue(word_count['30MINUTES'] == 0)

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('trackerian.Activity.return_current_duration')
    def test_name_grouped_duration_shown(self, mocked_duration, mocked_stdout):
        mocked_duration.return_value = datetime.timedelta(minutes=60)
        trackerian.print_summary(None)
        # Activity 3 given 1 min current duration so total isn't same as name
        self.assertIn('01:00:00', mocked_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('trackerian.Activity.return_current_duration')
    def test_name_grouped_percentage_printed(self, mocked_duration,
                                             mocked_stdout):
        mocked_duration.return_value = datetime.timedelta(minutes=15)
        trackerian.print_summary(None)
        # Activity 3 given 15 min current duration (20%)
        self.assertIn('20.00%', mocked_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_tags_printed(self, mocked_stdout):
        trackerian.print_summary(None)
        self.assertIn('TagOne', mocked_stdout.getvalue())
        self.assertIn('TagTwo', mocked_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('trackerian.Activity.return_current_duration')
    def test_tag_grouped_duration(self, mocked_duration, mocked_stdout):
        mocked_duration.return_value = datetime.timedelta(minutes=10)
        trackerian.print_summary(None)
        # Activity 3 given 10 minutes current duration so tag one = 01:10:00
        self.assertIn('01:10:00', mocked_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('trackerian.Activity.return_current_duration')
    def test_tag_grouped_percentage_printed(self, mocked_duration,
                                            mocked_stdout):
        mocked_duration.return_value = datetime.timedelta(hours=1)
        trackerian.print_summary(None)
        # Activity 3 given 1 hour so Tagtwo percentage will be (50.00%)
        self.assertIn('50.00%', mocked_stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_earlier_than_range_start_datetime_ignored(self, mocked_stdout):
        date_range_start = datetime.datetime.now()
        trackerian.Activity('Alone')
        trackerian.print_summary(date_range_start)
        self.assertNotIn('30Minutes', mocked_stdout.getvalue())


class TestEditActivity(unittest.TestCase):
    """Tests for edit_activity function."""

    def setUp(self):
        """Instantiate two Activity members one finished one running."""
        trackerian.Activity('Finished Activity')
        trackerian.Activity.instances[0].end_activity()
        trackerian.Activity('Running Activity')

    def tearDown(self):
        """Restore trackerian's Activity instances to an empty list."""
        trackerian.Activity.instances = []

    def test_name_arg_edits_name(self):
        trackerian.edit_activity(
            trackerian.Activity.instances[0], 'name', ['New']
        )
        self.assertEqual(trackerian.Activity.instances[0].name, 'New')

    def test_tag_arg_edits_tags(self):
        new_tags = ['List', 'Of', 'New', 'Tags']
        trackerian.edit_activity(
            trackerian.Activity.instances[1], 'tag', new_tags
        )
        self.assertEqual(trackerian.Activity.instances[1].tags, new_tags)

    @patch('trackerian.Activity.update_datetime')
    def test_end_arg_calls_update_with_right_args(self, mocked_update):
        trackerian.edit_activity(
            trackerian.Activity.instances[0], 'end', ['15:16:17']
        )
        self.assertEqual(mocked_update.call_args[0], ('end', '15:16:17'))

    @patch('trackerian.Activity.update_datetime')
    def test_start_arg_calls_update_with_right_args(self, mocked_update):
        trackerian.edit_activity(
            trackerian.Activity.instances[0], 'start', ['18:19:20']
        )
        self.assertEqual(mocked_update.call_args[0], ('start', '18:19:20'))


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

    @patch('trackerian.get_current_datetime')
    def test_end_variable_set_to_correct_datetime(self, mocked_time):
        end_datetime_object = datetime.datetime(2010, 10, 10, 10, 20, 00)
        mocked_time.return_value = end_datetime_object
        trackerian.Activity.instances[0].end_activity()
        end = trackerian.Activity.instances[0].end
        self.assertEqual(end, end_datetime_object)

    @patch('trackerian.get_current_datetime')
    def test_end_str_variable_set_correctly(self, mocked_time):
        end_datetime_object = datetime.datetime(2010, 10, 10, 10, 30, 00)
        mocked_time.return_value = end_datetime_object
        trackerian.Activity.instances[0].end_activity()
        end_str = trackerian.Activity.instances[0].end_str
        self.assertEqual(end_str, '10:30:00')

    @patch('trackerian.get_current_datetime')
    def test_duration_set_to_correct_timedelta(self, mocked_time):
        mocked_time.return_value = datetime.datetime(2010, 10, 10, 10, 40, 00)
        trackerian.Activity.instances[0].end_activity()
        duration = trackerian.Activity.instances[0].duration
        self.assertEqual(duration, datetime.timedelta(0, 1800))

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('trackerian.get_current_datetime')
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

    @patch('trackerian.get_current_datetime')
    def test_returns_accurate_timedelta_object(self, mocked_time):
        mocked_time.side_effect = [
            datetime.datetime(2012, 12, 12, 12, 30, 00),
            datetime.datetime(2012, 12, 12, 13, 00, 00)
        ]
        trackerian.Activity('Check Duration')
        duration = trackerian.Activity.instances[-1].return_current_duration()
        self.assertEqual(duration, datetime.timedelta(0, 1800))


class TestUpdateDatetimeActivityClassMethod(unittest.TestCase):
    """Tests for update_datetime method of Activity class."""

    def setUp(self):
        """Instantiate an activity for editing."""
        trackerian.Activity('To Edit')
        trackerian.Activity.instances[0].end_activity()

    def tearDown(self):
        """Restore trackerian's Activity instances to an empty list."""
        trackerian.Activity.instances = []

    def test_end_variable_updated_with_end_to_edit_argument_passed(self):
        trackerian.Activity.instances[0].update_datetime('end', '14:13:12')
        new_end = trackerian.Activity.instances[0].end.strftime('%H:%M:%S')
        self.assertEqual(new_end, '14:13:12')

    def test_start_variable_updated_with_start_to_edit_argument_passed(self):
        trackerian.Activity.instances[0].update_datetime('start', '17:18:19')
        new_start = trackerian.Activity.instances[0].start.strftime('%H:%M:%S')
        self.assertEqual(new_start, '17:18:19')

    def test_end_argument_updates_end_str_variable(self):
        trackerian.Activity.instances[0].update_datetime('end', '10:09:08')
        self.assertEqual(
            trackerian.Activity.instances[0].end_str, '10:09:08'
        )

    def test_start_argument_updates_start_str_variable(self):
        trackerian.Activity.instances[0].update_datetime('start', '05:06:07')
        self.assertEqual(
            trackerian.Activity.instances[0].start_str, '05:06:07'
        )

    def test_end_argument_updates_duration_variable(self):
        start = datetime.datetime.now().replace(
            hour=9, minute=0, second=0, microsecond=0
        )
        trackerian.Activity.instances[0].start = start
        trackerian.Activity.instances[0].update_datetime('end', '12:00:00')
        duration_timedelta = datetime.timedelta(hours=3)
        self.assertEqual(
            trackerian.Activity.instances[0].duration, duration_timedelta
        )

    def test_start_argument_updates_duration_variable(self):
        end = datetime.datetime.now().replace(
            hour=13, minute=0, second=0, microsecond=0
        )
        trackerian.Activity.instances[0].end = end
        trackerian.Activity.instances[0].update_datetime('start', '08:00:00')
        duration_timedelta = datetime.timedelta(hours=5)
        self.assertEqual(
            trackerian.Activity.instances[0].duration, duration_timedelta
        )


class TestStrFormatTimedelta(unittest.TestCase):
    """Test for str_format_timedelta function."""

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


class TestPercentageOfTimedelta(unittest.TestCase):
    """Tests for percentage_of_timedelta_function."""

    def test_returns_correct_percentage(self):
        total = datetime.timedelta(hours=1)
        duration = datetime.timedelta(minutes=15)
        self.assertEqual(
            trackerian.percentage_of_timedelta(total, duration), '25.00%'
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
        'summary': None,
        'list': False,
        'tag': None,
        'edit': None,
    }
    defaulted_args_dict[key] = new_value
    return defaulted_args_dict


if __name__ == '__main__':
    unittest.main()
