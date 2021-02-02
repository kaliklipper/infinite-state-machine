"""
Methods for handling DB creation and CRUD operations in MySql.
"""

# Standard library imports
import logging
import mysql.connector
from mysql.connector import errorcode

# Local application imports
from ism_dal.dao_interface import DAOInterface


class MySqlDAO(DAOInterface):

    cnx = None

    def __init__(self):
        self.logger = logging.getLogger('ism.mysql_dao.MySqlDAO')
        self.logger.info('Initialising MySqlDAO.')

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
        try:
            cursor = self.cnx.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            self.close_connection()
            return rows
        except mysql.connector.Error as err:
            self.logger.error(err.msg)

    def execute_sql_statement(self, sql):
        """Execute a SQL statement and return the exit code"""
        try:
            cursor = self.cnx.cursor()
            cursor.execute(sql)
            self.close_connection()
        except mysql.connector.Error as err:
            self.logger.error(err.msg)

    def open_connection(self, *args):
        """Opens a database connection.

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
                self.logger.error("Failed authentication to MYSql RDBMS")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                self.logger.error("Database does not exist")
            else:
                self.cnx.close()

    def open_connection_to_database(self, *args):
        """Opens a database connection to a specific database."""
        try:
            self.cnx = mysql.connector.connect(
                user=args[0]['database']['user'],
                host=args[0]['database']['host'],
                password=args[0]['database']['password'],
                database=args[0]["database"]["run_db"]
            )
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                self.logger.error("Failed authentication to MYSql RDBMS")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                self.logger.error("Database does not exist")
            else:
                self.cnx.close()

    def use_database(self, *args):
        """Switches to a database via a USE statement."""
        self.execute_sql_statement(f'USE {args[0]["database"]["db_name"]};')
