"""
Methods for handling DB creation and CRUD operations in Sqlite3.
"""

# Standard library imports
import logger
import sqlite3

# Local application imports
from ism_dal.dao_interface import DAOInterface


class Sqlite3DAO(DAOInterface):
    """Implements Methods for handling DB creation and CRUD operations against SQLITE3"""

    cnx = None
    db_path = None

    def close_connection(self):
        if self.cnx:
            self.cnx.close()

    def create_database(self, *args):
        """Calling open_connection creates the database in SQLITE3

        Seems redundant but is useful to honour the interface.
        """
        self.open_connection(*args)
        self.close_connection()

    def execute_sql_query(self, sql):
        """Execute a SQL query and return the cursor."""
        cursor = self.cnx.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        self.close_connection()
        return rows

    def execute_sql_statement(self, sql):
        """Execute a SQL statement and return the exit code"""
        cursor = self.cnx.cursor()
        cursor.execute(sql)
        self.cnx.commit()
        self.close_connection()

    def open_connection(self, *args):
        """Creates a database connection.

            * Creates a SQLITE3 database connection.
        """
        self.db_path = args[0]['database']['db_path']
        try:
            self.cnx = sqlite3.connect(self.db_path)
        except sqlite3.Error as error:
            logger.error("Error while connecting to sqlite", error)

    def use_database(self, *args):
        """Sqlite3 doesn't need this but implemented to honour interface."""
        pass
