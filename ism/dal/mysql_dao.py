"""
Methods for handling DB creation and CRUD operations in MySql.
"""

# Standard library imports
import logging
import mysql.connector
from mysql.connector import errorcode

# Local application imports
from ism.interfaces.dao_interface import DAOInterface


class MySqlDAO(DAOInterface):

    cnx = None
    host = None
    password = None
    run_db = None
    user = None

    def __init__(self, *args):
        self.logger = logging.getLogger('ism.mysql_dao.MySqlDAO')
        self.logger.info('Initialising MySqlDAO.')
        self.host = args[0]['database']['host']
        self.password = args[0]['database']['password']
        self.run_db = args[0]['database']['run_db']
        self.user = args[0]['database']['user']

    def close_connection(self):
        """Close the connection if open"""
        if self.cnx is not None:
            self.cnx.close()

    def create_database(self, *args):
        """Create the control database."""
        self.open_connection(*args)
        sql = f'CREATE DATABASE {args[0]["database"]["run_db"]}'
        try:
            cursor = self.cnx.cursor()
            cursor.execute(sql)
            self.close_connection()
        except mysql.connector.Error as err:
            self.logger.error(err.msg)

    def execute_sql_query(self, sql):
        """Execute a SQL query and return the cursor.

        Assumes DB is already created.
        """
        try:
            self.open_connection_to_database()
            cursor = self.cnx.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            self.close_connection()
            return rows
        except mysql.connector.Error as err:
            self.logger.error(err.msg)

    def execute_sql_statement(self, sql):
        """Execute a SQL statement

        Assumes DB is already created.
        """
        try:
            self.open_connection_to_database()
            cursor = self.cnx.cursor()
            cursor.execute(sql)
            self.cnx.commit()
            self.close_connection()
        except mysql.connector.Error as err:
            self.logger.error(err.msg)

    def open_connection(self, *args):
        """Opens a database connection.

            * MYSQL Creates a database in the MySql RDBMS.
            Assumes MySql installed.
        """
        try:
            self.cnx = mysql.connector.connect(
                user=self.user,
                host=self.host,
                password=self.password
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
                user=self.user,
                host=self.host,
                password=self.password,
                database=self.run_db
            )
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                self.logger.error("Failed authentication to MYSql RDBMS")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                self.logger.error("Database does not exist")
            else:
                self.cnx.close()
