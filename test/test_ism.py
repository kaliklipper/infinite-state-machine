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
import re
import unittest

# Local application imports
from infinite_state_machine.ISM import InfiniteStateMachine


class TestISM(unittest.TestCase):

    path_sep = os.path.sep
    dir = os.path.dirname(os.path.abspath(__file__))
    sqlite3_properties = f'{dir}{path_sep}sqlite3_properties.yaml'
    mysql_properties = f'{dir}{path_sep}mysql_properties.yaml'

    def test_properties_file_set(self):
        """Test that ISM sets path to the test file."""
        args = {
            'properties_file': self.sqlite3_properties
        }
        ism = InfiniteStateMachine(args)
        self.assertEqual(ism.properties_file, self.sqlite3_properties)

    def test_properties_are_read_in(self):
        """Test that it imports properties from the test file."""
        args = {
            'properties_file': self.sqlite3_properties
        }
        ism = InfiniteStateMachine(args)
        self.assertEqual(
            ism.properties['database']['password'],
            None,
            f'Unexpected result for database: key read from properties file ({self.sqlite3_properties})'
        )

    def test_sqlite3_database_creation(self):
        """Test that the sqlite3 database is created.

        Implies that rdbms key in properties is set to sqlite3 and sqlite3 installed.
        """
        args = {
            'properties_file': self.sqlite3_properties
        }
        ism = InfiniteStateMachine(args)
        self.assertTrue(os.path.exists(ism.get_database_name()), 'Sqlite3 database creation failed')

    def test_mysql_database_creation(self):
        """Test that the MySql database is created.

        Implies that rdbms key in properties is set to mysql and mysql installed.
        """
        args = {
            'properties_file': self.mysql_properties,
            'database': {
                'password': 'wbA7C2B6R7'
            }
        }
        ism = InfiniteStateMachine(args)
        db_name = ism.get_database_name()
        self.assertTrue(re.match(r'default_.+', db_name), 'Mysql DB name faile dto match expected pattern')


if __name__ == '__main__':
    unittest.main()
