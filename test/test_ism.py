"""
This module unit tests the Infinite State Machine.

The module contains the following functions:
    * test_properties_file_set - Test the setting of the ISM's
    property that holds the path to the properties file.
    * test_properties_are_read_in - Test that the values in the
    properties file are read in correctly.

"""

# Standard library imports
import os
import unittest

# Local application imports
from infinite_state_machine.ISM import InfiniteStateMachine


class TestISM(unittest.TestCase):

    path_sep = os.path.sep
    dir = os.path.dirname(os.path.abspath(__file__))
    props_path = f'{dir}{path_sep}test_properties.yaml'

    def test_properties_file_set(self):
        """Test that ISM sets path to the test file."""
        ism = InfiniteStateMachine(self.props_path)
        self.assertEqual(ism.props_file, self.props_path)

    def test_properties_are_read_in(self):
        """Test that it imports properties from the test file."""
        ism = InfiniteStateMachine(self.props_path)
        self.assertDictEqual(ism.properties['database'], {'rdbms': 'sqlite3', 'db_name': 'ism_db'})

    def test_sqlite3_database_creation(self):
        """Test that the sqlite3 database is created.

        Implies that rdbms key in properties is set to sqlite3 and sqlite3 installed.
        """
        ism = InfiniteStateMachine(self.props_path)


if __name__ == '__main__':
    unittest.main()
