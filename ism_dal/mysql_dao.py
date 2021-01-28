"""
Methods for handling DB creation and CRUD operations in MySql.
"""

# Standard library imports
import mysql.connector
from mysql.connector import errorcode

# Local application imports
from ism_dal.dao_interface import DAOInterface


class MySqlDAO(DAOInterface):

    cnx = None

    def close_connection(self):
        """Close the connection if open"""
        if self.cnx is not None:
            self.cnx.close()

    def create_database(self, *args):
        """Create the control database."""
        self.open_connection(*args)
        sql = f'CREATE DATABASE {args[0]["database"]["run_db"]}'
        self.execute_sql_statement(sql)
        self.close_connection()

    def execute_sql_query(self, sql):
        """Execute a SQL query and return the cursor."""
        pass

    def execute_sql_statement(self, sql):
        """Execute a SQL statement and return the exit code"""
        db_cursor = self.cnx.cursor()
        db_cursor.execute(sql)

    def open_connection(self, *args):
        """Creates or opens a database connection.

            * MYSQL Creates a database in the MySql RDBMS. Assumes MySql installed.
        """
        try:
            self.cnx = mysql.connector.connect(
                user=args[0]['database']['user'],
                host=args[0]['database']['host'],
                password=args[0]['database']['password']
            )
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with the user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                self.cnx.close()
