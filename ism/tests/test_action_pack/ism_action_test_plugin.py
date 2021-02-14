"""Express a test action for the unit tests

"""
from ism.core.action import Action


class ISMActionTestPlugin(Action):
    """Action creates a test file in tmp then exits


    Unit tests can check for existence of file to confirm
    that the action ran. Existence of only one instance proves
    action exits after one pass.
    """
    pass
