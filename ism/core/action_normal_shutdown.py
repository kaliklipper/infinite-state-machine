"""Process a normal shutdown

"""

from ism.core.base_action import BaseAction


class ActionNormalShutdown(BaseAction):

    def execute(self):
        """For now the emergency and ordinary shutdown is the same"""

        if self.active():

            self.properties['running'] = False
            self.deactivate()
