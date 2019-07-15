#!/usr/bin/env python3

""" User Story Testing for  Trackerian - a commandline time tracker."""

from datetime import datetime
import io
import sys
import unittest
import unittest.mock
from unittest.mock import call, patch

import trackerian


class TestParseArguments(unittest.TestCase):

    # User runs trackerian.py from commandline and receives help instructions
    def test_no_argument_prints_help(self):
        """Test the response of invoking the program with no arguments."""
        captured_output = io.StringIO()
        sys.stdout = captured_output
        trackerian.parse_arguments([])

        self.assertIn("usage:", captured_output.getvalue())

    # From help finds that --begin TASKNAME is how to start timing a task
    def test_begin_argument_stores_activity_name_in_return(self):
        """Test that using begin with keyword results in dict entry for it."""
        args = trackerian.parse_arguments(['--begin', 'Activity Name'])

        self.assertEqual({'begin': 'Activity Name'}, args)


class TestBeginActivityFunction(unittest.TestCase):

    def test_begin_activity_writes_activity_name_to_file(self):
        """."""
        output_file = io.StringIO()
        trackerian.begin_activity('Activity Name', output_file)
        output_file.seek(0)
        written = output_file.read()

        self.assertIn('Activity Name', written)

    @patch('trackerian.get_current_time_and_format')
    def test_begin_activity_writes_date_and_time_to_file(self, mocked_date):
        """."""
        mocked_date.return_value = '2000-02-20 10:10:01'
        output_file = io.StringIO()
        trackerian.begin_activity('Activity Name', output_file)
        output_file.seek(0)
        written = output_file.read()

        self.assertIn('2000-02-20 10:10:01', written)


if __name__ == '__main__':
    unittest.main()

