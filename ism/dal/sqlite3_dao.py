"""
Methods for handling DB creation and CRUD operations in Sqlite3.
"""

# Standard library imports
import logging
import sqlite3

# Local application imports
from ism.exceptions.exceptions import UnrecognisedParameterisationCharacter
from ism.interfaces.dao_interface import DAOInterface


class Sqlite3DAO(DAOInterface):
    """Implements Methods for handling DB creation and CRUD operations against SQLITE3"""

    def __init__(self, *args):
        self.db_path = args[0]['database']['db_path']
        self.raise_on_sql_error = args[0].get('database', {}).get('raise_on_sql_error', False)
        self.logger = logging.getLogger('ism.sqlite3_dao.Sqlite3DAO')
        self.logger.info('Initialising Sqlite3DAO.')
        self.cnx = None

    def close_connection(self):
        if self.cnx:
            self.cnx.close()

    def create_database(self, *args):
        """Calling open_connection creates the database in SQLITE3

        Seems redundant but is useful to honour the interface.
        """

        self.open_connection(*args)
        self.close_connection()

    def execute_sql_query(self, sql, params=()):
        """Execute a SQL query and return the result.

        @:param query. { sql: 'SELECT ...', params: params
        """
        try:
            self.open_connection()
            cursor = self.cnx.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            self.close_connection()
            return rows
        except sqlite3.Error as e:
            logging.error(f'Error executing sql query ({sql}) ({params}): {e}')
            if self.raise_on_sql_error:
                raise e

    def execute_sql_statement(self, sql, params=()):
        """Execute a SQL statement and return the exit code"""
        try:
            self.open_connection()
            cursor = self.cnx.cursor()
            cursor.execute(sql, params)
            self.cnx.commit()
            self.close_connection()
        except sqlite3.Error as e:
            logging.error(f'Error executing sql query ({sql}) ({params}): {e}')
            if self.raise_on_sql_error:
                raise e

    def open_connection(self, *args) -> sqlite3.Connection:
        """Creates a database connection.

        Opens a SQLITE3 database connection and returns a connector.
        """
        try:
            self.cnx = sqlite3.connect(self.db_path)
            return self.cnx
        except sqlite3.Error as error:
            self.logger.error("Error while connecting to Sqlite3 database.", error)

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
            return sql.replace('%s', '?')
        elif '?' in sql:
            return sql
        else:
            raise UnrecognisedParameterisationCharacter(
                f'Parameterisation character not recognised / found in SQL string ({sql})'
            )
