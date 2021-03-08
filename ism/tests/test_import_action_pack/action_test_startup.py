"""Express a test action for the unit tests

"""
from ism.core.base_action import BaseAction


class ActionTestPlugin(BaseAction):
    """Action creates a test file in tmp then exits


    Unit tests can check for existence of file to confirm
    that the action ran. Existence of only one instance proves
    action exits after one pass.
    """

    def execute(self):

        if self.active():

            with open('/tmp/test_import_action_pack.txt', 'w') as test_file:
                test_file.write('Test string from class ISMActionTestPlugin(BaseAction)\n')

            self.deactivate()
