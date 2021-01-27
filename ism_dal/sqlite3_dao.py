"""
Methods for handling DB creation and CRUD operations.
"""

# Standard library imports
import sqlite3

# Local application imports
from ism_dal.dao_interface import DAOInterface


class Sqlite3(DAOInterface):
    """Implements Methods for handling DB creation and CRUD operations against SQLITE3"""

    connection = None
    db_path = None

    def close_connection(self):
        if self.connection:
            self.connection.close()

    def create_database(self, *args):
        """Calling open_connection creates the database in SQLITE3

        Seems redundant but is useful to honour the interface.
        """
        self.open_connection(*args)
        self.close_connection()

    def execute_sql_query(self, sql):
        """Execute a SQL query and return the cursor."""
        pass

    def execute_sql_statement(self, sql):
        """Execute a SQL statement and return the exit code"""
        pass

    def open_connection(self, *args):
        """Creates a database connection.

            * Creates a SQLITE3 database connection.
        """
        self.db_path = args[0]

        try:
            self.connection = sqlite3.connect(self.db_path)
            return self.connection

        except sqlite3.Error as error:
            print("Error while connecting to sqlite", error)
