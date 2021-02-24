"""
Methods for handling DB creation and CRUD operations in MySql.
"""

# Standard library imports
import logging
import mysql.connector
from mysql.connector import errorcode

# Local application imports
from ism.exceptions.exceptions import UnrecognisedParameterisationCharacter, ExecutionPhaseNotFound
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
        self.raise_on_sql_error = args[0].get('database', {}).get('raise_on_sql_error', False)

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

    def execute_sql_query(self, sql, params=()):
        """Execute a SQL query and return the result.

        Assumes DB is already created.
        """
        try:
            self.open_connection_to_database()
            cursor = self.cnx.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            self.close_connection()
            return rows
        except mysql.connector.Error as err:
            self.logger.error(err.msg)
            if self.raise_on_sql_error:
                raise err

    def execute_sql_statement(self, sql, params=()):
        """Execute a SQL statement

        Assumes DB is already created.
        """
        try:
            self.open_connection_to_database()
            cursor = self.cnx.cursor()
            cursor.execute(sql, params)
            self.cnx.commit()
            self.close_connection()
        except mysql.connector.Error as err:
            self.logger.error(err.msg)
            if self.raise_on_sql_error:
                raise err

    def open_connection(self, *args) -> mysql.connector.connection_cext.CMySQLConnection:
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
            return self.cnx
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

    @staticmethod
    def prepare_parameterised_statement(sql: str) -> str:
        """Prepare a parameterised sql statement for this RDBMS.

        Third party developers will want to use the DAO to run CRUD
        operations against the DB, but we support multiple RDBMS. e.g.

        MySql: INSERT INTO Employee
                       (id, Name, Joining_date, salary) VALUES (%s,%s,%s,%s)
        Sqlite3: INSERT INTO Employee
                       (id, Name, Joining_date, salary) VALUES (?,?,?,?)

        This method ensures that the parameterisation is set correctly
        for the RDBMS in use. Method doesn't use very vigorous checking but
        as this should only be an issue while developing a new action pack
        it should be sufficient for now.
        """

        if '%s' in sql:
            return sql
        elif '?' in sql:
            return sql.replace('?', '%s')
        else:
            raise UnrecognisedParameterisationCharacter(
                f'Parameterisation character not recognised / found in SQL string ({sql})'
            )

    def get_execution_phase(self) -> str:
        """Get the current active execution phase.

        e.g.
            * RUNNING
            * STARTING
            * EMERGENCY_SHUTDOWN
            * NORMAL_SHUTDOWN
            * STOPPED
        """
        try:
            return self.execute_sql_query(
                f'SELECT execution_phase FROM phases WHERE state = 1'
            )[0][0]
        except IndexError as e:
            raise ExecutionPhaseNotFound(f'Current execution_phase not found in control database. ({e})')