#!/usr/bin/env python3

""" User Story Testing for  Trackerian - a commandline time tracker."""

import io
import sys
import unittest
from unittest.mock import call, patch

import trackerian


class TestParseArguments(unittest.TestCase):
# User runs trackerian.py from commandline and receives help instructions
    def test_no_argument_prints_help(self):
        """Test the response of invoking the program with no arguments."""
        captured_output = io.StringIO()
        sys.stdout = captured_output
        trackerian.parse_arguments()
        self.assertIn("usage:", captured_output.getvalue())



if __name__ == '__main__':
    unittest.main()

