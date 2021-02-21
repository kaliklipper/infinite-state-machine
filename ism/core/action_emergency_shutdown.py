"""Process an emergency shutdown

"""

from ism.core.base_action import BaseAction


class ActionEmergencyShutdown(BaseAction):

    def execute(self):
        """Emergency shutdown means just kill the main thread."""

        if self.active():

            self.set_execution_phase('EMERGENCY_SHUTDOWN')
            self.properties['running'] = False
            self.deactivate()
