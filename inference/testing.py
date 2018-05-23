# (c) 2018 Dean Stamler

import os, sys
import unittest
from datetime import datetime
from inference.inference import snap_to_bound, infer

# Make the parent directory the first element of sys.path so we can run
#
#       'python -m unittest -v testing'
#
# in the 'inference' directory to run the tests. In iPython or REPL use
#
#       'unittest.main(verbosity=2,exit=False)'
#
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



class TestInferenceFunctions(unittest.TestCase):

    def test_snap_to_bound(self):

        # TODO: Ensure testing has complete branch coverage

        lower_bound = datetime(year=2010, month=6, day=2, hour=8, minute=30)

        # Test lower_bound condition with both choices out of bounds
        raw_date_string = "3/4/2010 8:32:06 AM"
        with self.assertRaises(ValueError):
            snap_to_bound(raw_date_string, lower_bound, False)

        # Test lower_bound condition with one choice out of bound
        raw_date_string = "2/7/2010 8:32:00 AM"
        actual_date = datetime(year=2010, month=7, day=2, hour=8, minute=32)
        self.assertEqual(actual_date, snap_to_bound(raw_date_string,lower_bound,False),"Failed when one option out of bounds")

        # Test lower_bound condition with both choices in bounds
        raw_date_string = "8/7/2010 8:32:00 AM"
        actual_date = datetime(year=2010, month=7, day=8, hour=8, minute=32)
        self.assertEqual(actual_date, snap_to_bound(raw_date_string,lower_bound,False),"Failed when both options in bounds")

    def test_infer(self):

        # TODO: Ensure testing has complete branch coverage

        # Ascending mode tests
        ######################

        string_list = ["08/04/2013 7:58:32 AM", "09/04/2013 7:54:18 AM",
                            "09/04/2013 1:11:20 PM", "12/04/2013 7:02:46 AM",
                            "12/04/2013 9:53:43 AM"]
        output_list = [
            datetime(year=2013, month=4, day=8, hour=7, minute=58, second=32),
            datetime(year=2013, month=4, day=9, hour=7, minute=54, second=18),
            datetime(year=2013, month=4, day=9, hour=13, minute=11, second=20),
            datetime(year=2013, month=4, day=12, hour=7, minute=2, second=46),
            datetime(year=2013, month=4, day=12, hour=9, minute=53, second=43),
        ]
        lower_bound = datetime(year=2013, month=4, day=7)
        upper_bound = datetime(year=2013, month=4, day=18)

        # Test both lower_bound and upper_bound missing
        with self.assertRaises(ValueError):
            infer(None, None, string_list)

        # Test both bounds provided
        self.assertEqual(output_list, infer(lower_bound, upper_bound,string_list), "Failed when both bounds provided")

        # Test lower_bound only provided
        self.assertEqual(output_list, infer(lower_bound, None, string_list), "Failed when only lower_bound provided")

        # Test upper_bound only provided
        self.assertEqual(output_list, infer(None, upper_bound, string_list), "Failed when only upper_bound provided")

        # Descending mode tests
        #######################

        string_list.reverse()
        output_list.reverse()
        descending = True

        # Test both lower_bound and upper_bound missing
        with self.assertRaises(ValueError):
            infer(None, None, string_list)

        # Test both bounds provided
        self.assertEqual(output_list, infer(lower_bound, upper_bound,string_list, descending), "Failed when both bounds provided")

        # Test lower_bound only provided
        self.assertEqual(output_list, infer(lower_bound, None, string_list, descending), "Failed when only lower_bound provided")

        # Test upper_bound only provided
        self.assertEqual(output_list, infer(None, upper_bound, string_list, descending), "Failed when only upper_bound provided")
