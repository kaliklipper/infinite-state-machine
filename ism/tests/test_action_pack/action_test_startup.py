"""Express a test action for the unit tests

"""
from ism.core.base_action import BaseAction


class ISMActionTestPlugin(BaseAction):
    """Action creates a test file in tmp then exits


    Unit tests can check for existence of file to confirm
    that the action ran. Existence of only one instance proves
    action exits after one pass.
    """

    def execute(self):
        x = 0
        pass
