"""Check that the ISM bootstraps and arrives at a fit state to run

"""
from ism.core.action import Action


class ActionConfirmReadyToRun(Action):
    """Check if we're ready to run and if so, change state.

    Ready if:
        All BEFORE actions (if any) have completed.
    """

    def execute(self):
        """Execute the instructions for this action"""
        if self.active():
            sql = self.dao.prepare_parameterised_statement(
                f'SELECT action FROM actions WHERE action LIKE "%Before%" AND active = ?'
            )
            records = self.dao.execute_sql_query(sql, (True,))
            if len(records) > 0:
                return
            else:
                # Change phase from STARTING to RUNNING
                sql = self.dao.prepare_parameterised_statement(
                    f'UPDATE phases SET state = ? WHERE state = ?'
                )
                self.dao.execute_sql_statement(sql, (False, True))
                sql = self.dao.prepare_parameterised_statement(
                    f'UPDATE phases SET state = ? WHERE execution_phase = "RUNNING";'
                )
                self.dao.execute_sql_statement(sql, (True,))
                self.activate('ActionProcessInboundMessages')
                # Ready to run so we're done with this action
                self.deactivate()
