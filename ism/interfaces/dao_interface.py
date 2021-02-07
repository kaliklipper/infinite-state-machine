"""
Interface defines required methods for a Data Access Layer.
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

    def execute_sql_statement(self, sql, close_cnx=True):
        """Execute a SQL statement and return the exit code"""
        pass

    def open_connection(self, *args):
        """Creates a database connection"""
        pass

    def open_connection_to_database(self, *args):
        """Creates a connection to the specific DB"""
        pass
