"""Check that the ISM bootstraps and arrives at a fit state to run

"""
from ism.core.base_action import BaseAction


class ActionConfirmReadyToRun(BaseAction):
    """Check if we're ready to run and if so, change state.

    Ready if:
        All ActionBefore actions (if any) have completed.
    """

    def execute(self):
        """Execute the instructions for this action"""
        if self.active():

            sql = self.dao.prepare_parameterised_statement(
                f'SELECT action FROM actions WHERE action LIKE "ActionBefore%" AND active = ?'
            )
            records = self.dao.execute_sql_query(sql, (True,))
            if len(records) > 0:
                return
            else:
                # Change phase from STARTING to RUNNING
                self.set_execution_phase('RUNNING')
                # Start reacting to messages
                self.activate('ActionProcessInboundMessages')
                # Ready to run so we're done with this action
                self.deactivate()
