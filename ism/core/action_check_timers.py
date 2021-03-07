"""Check if any timers are running

Using the standard python timer objects to run an action after a specified time
in another thread would not conform to the state machine paradigm.

So this action runs every iteration of the action stack and checks to see if any
 actions have been set to run after a specific time. The actual interval is not guaranteed,
 as the other actions in the stack might be running at that time. The only guarantee is that
 the specified interval will definitely have expired before the action is run.

"""

from ism.core.base_action import BaseAction


class ActionCheckTimers(BaseAction):

    def execute(self):
        """Check to see if any timers have been set and if expired, enable the action in it's payload."""

        if self.active():

            epoch_millis = self.get_epoch_milliseconds()
            sql = self.dao.prepare_parameterised_statement(
                f'SELECT action, payload, expiry FROM timers WHERE active = ?'
            )
            # Check if active timer/s have expired
            for timer in self.dao.execute_sql_query(sql, (True,)):
                if timer[2] < epoch_millis:
                    # Timer has expired so enable the action
                    self.set_payload(timer[0], timer[1])
                    self.activate(timer[0])
