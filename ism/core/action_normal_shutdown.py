"""Process a normal shutdown

"""

from ism.core.base_action import BaseAction


class ActionNormalShutdown(BaseAction):

    def execute(self):
        """Normal shutdown so activate ActionConfirmReadyToStop"""

        if self.active():

            self.set_execution_phase('NORMAL_SHUTDOWN')
            self.activate('ActionConfirmReadyToStop')
            self.deactivate()
