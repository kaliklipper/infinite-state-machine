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
            sql = f'SELECT action FROM actions WHERE action LIKE "%Before%" AND active = {True};'
            records = self.dao.execute_sql_query(sql)
            if len(records) > 0:
                return
            else:
                # Change phase from STARTING to RUNNING
                sql = f'UPDATE phases SET state = {False} WHERE state = {True};'
                self.dao.execute_sql_statement(sql)
                sql = f'UPDATE phases SET state = {True} WHERE phase_name = "RUNNING";'
                self.dao.execute_sql_statement(sql)
                self.activate('ActionProcessInboundMessages')
                # Ready to run so we're done with this action
                self.deactivate()
