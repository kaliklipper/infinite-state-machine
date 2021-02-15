"""Parent Action class

"""
import logging

from ism.exceptions.exceptions import DuplicateDataInControlDatabase, MissingDataInControlDatabase


class Action:

    def __init__(self, *args):
        self.action_name = self.__class__.__name__
        self.dao = args[0]['dao']
        self.properties = args[0]['properties']
        self.logger = logging.getLogger(f'{self.action_name}')

    def active(self) -> bool:
        """Test if the child action is activated"""
        action = self.dao.execute_sql_query(
            f'SELECT active, run_phase FROM actions WHERE action = "{self.action_name}";'
        )
        phase = self.dao.execute_sql_query(
            f'SELECT phase_name FROM phases WHERE state = 1;'
        )
        if len(action) > 1:
            message = f'Duplicate records for action {self.action_name} found'
            self.logger.error(message)
            raise DuplicateDataInControlDatabase(message)

        if len(action) == 0:
            message = f'Missing record for action {self.action_name}'
            self.logger.error(message)
            raise MissingDataInControlDatabase(message)

        if action[0][1] == phase[0][0]:
            if action[0][0]:
                return True

        return False

    def activate(self, action: str):
        """Activate the named action"""

        # TODO Add check for correct run phase before activating.
        sql = f'UPDATE actions SET active = {True} WHERE action = "{action}";'

        self.dao.execute_sql_statement(sql)

    def deactivate(self, action=None):
        """Deactivate the named action or this action by default"""

        if action is None:
            sql = f'UPDATE actions SET active = {False} WHERE action = "{self.action_name}";'
        else:
            sql = f'UPDATE actions SET active = {False} WHERE action = "{action}";'

        self.dao.execute_sql_statement(sql)
