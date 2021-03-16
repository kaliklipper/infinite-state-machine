"""Parent Action class

"""
import logging
import time

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
            # If the action is set to active
            if this_action[0][0]:
                # If the execution phase for the child matches the current phase
                if this_action[0][1] == phase or this_action[0][1] == 'ALL':
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

    def clear_payload(self):
        """Clear the child action's payload"""
        sql = self.dao.prepare_parameterised_statement(
            'UPDATE actions SET payload = NULL WHERE action = ?'
        )
        self.dao.execute_sql_statement(
            sql,
            (self.action_name,)
        )

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

    @staticmethod
    def get_epoch_milliseconds() -> int:
        return int(time.time()*1000.0)

    def get_payload(self) -> list:
        """Get the payload for the child action"""

        sql = self.dao.prepare_parameterised_statement(
            'SELECT payload FROM actions WHERE action = ?'
        )
        return self.dao.execute_sql_query(
            sql,
            (self.action_name,)
        )

    def set_execution_phase(self, execution_phase: str):

        if execution_phase not in ["STARTING", 'RUNNING', 'EMERGENCY_SHUTDOWN', 'NORMAL_SHUTDOWN', 'STOPPED']:
            raise ExecutionPhaseUnrecognised(f'Unrecognised execution_phase - ({execution_phase}).')

        sql = self.dao.prepare_parameterised_statement(
            f'UPDATE phases SET state = ? WHERE state = ?'
        )
        self.dao.execute_sql_statement(sql, (False, True))
        sql = self.dao.prepare_parameterised_statement(
            f'UPDATE phases SET state = ? WHERE execution_phase = ?;'
        )
        self.dao.execute_sql_statement(sql, (True, execution_phase))

    def set_payload(self, action: str, payload: str):
        """Set the payload for the action named in the params.

        :param action The name of the action to trigger.
        :param payload JSON payload for the action.
        """
        sql = self.dao.prepare_parameterised_statement(
            'UPDATE actions SET payload = ? WHERE action = ?'
        )
        self.dao.execute_sql_statement(
            sql,
            (
                payload,
                action
            )
        )

    def set_timer(self, action: str, payload: str, expiry: int):
        """Set a timer to trigger an action after expiry
        :param action The name of the action to trigger.
        :param payload JSON payload for the action.
        :param expiry Time in epoch milliseconds that the timer will expire,
        """

        sql = self.dao.prepare_parameterised_statement(
            'UPDATE timers SET action = ?, payload = ?, expiry = ?'
        )
        self.dao.execute_sql_statement(
            sql,
            (
                action,
                payload,
                expiry
            )
        )

    @staticmethod
    def set_timer_expiry(hours=None, seconds=None, milliseconds=None) -> int:
        """Calculate the expiry time for a timer, offset from now

        :param hours The interval expressed in hours
        :param seconds The interval expressed in seconds
        :param milliseconds The interval expressed in milliseconds
        :return Expiry time in milliseconds
        """

        if hours:
            return int((time.time() * 1000) + (hours * 60 * 60 * 1000))
        elif seconds:
            seconds *= 1000
            return int((time.time() * 1000) + seconds)
        elif milliseconds:
            return int((time.time() * 1000) + milliseconds)
        else:
            raise RuntimeError('Duration expected but got None')

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
