#!/usr/bin/env python3

""" User Story Testing for  Trackerian - a commandline time tracker."""

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


class TestArgumentFunctionCalls(unittest.TestCase):

    # User begins timing a new activity by passing --begin argument
    @patch('trackerian.begin_activity')
    @patch('trackerian.parse_arguments')
    def test_begin_activity_called(self, mocked_parse, mocked_begin):
        """."""
        mocked_parse.return_value = {'begin': 'Activity Name'}
        trackerian.main()

        self.assertTrue(mocked_begin.called)


class TestBeginActivityFunction(unittest.TestCase):

    pass

if __name__ == '__main__':
    unittest.main()

