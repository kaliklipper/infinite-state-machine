"""Check that the ISM bootstraps and arrives at a fit state to run

"""
from ism.core.base_action import BaseAction


class ActionConfirmReadyToStop(BaseAction):
    """Check if we're ready to run and if so, change state.

    Ready if:
        All BEFORE actions (if any) have completed.
    """

    def execute(self):
        """Execute the instructions for this action"""
        if self.active():

            sql = self.dao.prepare_parameterised_statement(
                f'SELECT action FROM actions WHERE action LIKE "%After%" AND active = ?'
            )
            records = self.dao.execute_sql_query(sql, (True,))
            if len(records) > 0:
                return
            else:
                # Change phase from to RUNNING to STOPPED
                self.set_execution_phase('STOPPED')
                # Stop the main thread
                self.properties['running'] = False
                # Ready to stop so we're done with this action
                self.deactivate()
