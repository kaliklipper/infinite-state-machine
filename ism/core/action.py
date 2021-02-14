"""Parent Action class

"""
import logging


class Action:

    properties = None
    dao = None
    logger = None

    def __init__(self):
        self.action_name = self.__class__.__name__

    def active(self) -> bool:
        """Test if the child action is activated"""
        action = self.dao.execute_sql_query(
            f'SELECT active, run_phase FROM actions WHERE action = "{self.action_name}";'
        )
        phase = self.dao.execute_sql_query(
            f'SELECT phase_name FROM phases WHERE state = 1;'
        )
        x = 0
        pass

    def activate(self, action: str):
        """Activate the named action"""
        pass

    def deactivate(self, action):
        """Deactivate the named action"""
        pass
