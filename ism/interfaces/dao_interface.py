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

    def execute_sql_query(self, sql, params=()):
        """Execute a SQL query and return the result."""
        pass

    def execute_sql_statement(self, sql, params=()):
        """Execute a SQL statement and return the exit code"""
        pass

    def open_connection(self, *args):
        """Creates a database connection"""
        pass

    def open_connection_to_database(self, *args):
        """Creates a connection to the specific DB"""
        pass

    @staticmethod
    def prepare_parameterised_statement(sql: str) -> str:
        """Prepare a parameterised sql statement for this RDBMS."""
        pass
