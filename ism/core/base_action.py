"""Parent Action class

"""
import logging

from ism.exceptions.exceptions import DuplicateDataInControlDatabase, MissingDataInControlDatabase, \
    ExecutionPhaseNotFound, ExecutionPhaseUnrecognised


class BaseAction:

    def __init__(self, *args):
        self.action_name = self.__class__.__name__
        self.dao = args[0]['dao']
        self.properties = args[0]['properties']
        self.logger = logging.getLogger(f'{self.action_name}')

    def active(self) -> bool:
        """Test if the child action is activated"""

        sql = self.dao.prepare_parameterised_statement(
            f'SELECT active, execution_phase FROM actions WHERE action = ?'
        )
        this_action = self.dao.execute_sql_query(sql, (self.action_name,))
        phase = self.__get_execution_phase()

        if len(this_action) > 1:
            message = f'Duplicate records for action {self.action_name} found'
            self.logger.error(message)
            raise DuplicateDataInControlDatabase(message)

        if len(this_action) == 0:
            message = f'Missing record for action {self.action_name}'
            self.logger.error(message)
            raise MissingDataInControlDatabase(message)

        try:
            if this_action[0][0]:
                if this_action[0][1] == phase:
                    return True
            return False
        except Exception as e:
            self.logger.error(
                f'Error while testing action ({self.action_name}) execution phase. ({e})'
            )
            raise

    def activate(self, action: str):
        """Activate the named action"""

        sql = self.dao.prepare_parameterised_statement(f'UPDATE actions SET active = ? WHERE action = ?')
        params = (True, action)
        self.dao.execute_sql_statement(sql, params)

    def deactivate(self, action=None):
        """Deactivate the named action or this action by default"""

        sql = self.dao.prepare_parameterised_statement(
            f'UPDATE actions SET active = ? WHERE action = ?'
        )
        if action is None:
            params = (False, self.action_name)
        else:
            params = (False, action)

        self.dao.execute_sql_statement(sql, params)

    def set_execution_phase(self, execution_phase):

        if execution_phase not in ["STARTING", 'RUNNING', 'EMERGENCY_SHUTDOWN', 'NORMAL_SHUTDOWN', 'STOPPED']:
            raise ExecutionPhaseUnrecognised(f'Unrecognised execution_phase - ({execution_phase}).')

        sql = self.dao.prepare_parameterised_statement(
            f'UPDATE phases SET state = ? WHERE state = ?'
        )
        self.dao.execute_sql_statement(sql, (False, True))
        sql = self.dao.prepare_parameterised_statement(
            f'UPDATE phases SET state = ? WHERE execution_phase = "RUNNING";'
        )
        self.dao.execute_sql_statement(sql, (True,))

    # Private methods
    def __get_execution_phase(self) -> str:
        """Get the current active execution phase.

        e.g.
            * RUNNING
            * STARTING
            * EMERGENCY_SHUTDOWN
            * NORMAL_SHUTDOWN
            * STOPPED
        """
        try:
            return self.dao.execute_sql_query(
                f'SELECT execution_phase FROM phases WHERE state = 1'
            )[0][0]
        except IndexError as e:
            raise ExecutionPhaseNotFound(f'Current execution_phase not found in control database. ({e})')
