"""
Interface defines each data access object's methods.
"""


class DAOInterface:

    def close_connection(self):
        """Close the connection if open"""
        pass

    def create_database(self, *args):
        """Create the control database."""
        pass

    def execute_sql_query(self, sql):
        """Execute a SQL query and return the cursor."""
        pass

    def execute_sql_statement(self, sql):
        """Execute a SQL statement and return the exit code"""
        pass

    def open_connection(self, *args):
        """Creates or opens a database connection.

            * SQLITE3 Creates a database instance in the file system if not existing.
            * MYSQL Creates a database in the MySql RDBMS. Assumes MySql installed.
        """
        pass

    def use_database(self, *args):
        """Switches to a database via a USE statement."""
        pass
