"""
Module contains the state machine runner itself.

Implements the following functions:
    * __init__ - Constructor accepts path to properties file and
    then calls get_properties() to load the YAML.
    * get_properties - Read the properties file into the properties attribute.
    * run - Iterates over the array of imported actions and calls each one's
        execute method.
"""

# Standard library imports
import yaml


class InfiniteStateMachine:
    """
    Implements an Infinite State Machine

    Attributes
    ----------
    props_file: str
        Fully qualified path to the properties file.

    Methods
    -------
    run()
        Iterates over the array of actions and calls each one's
        execute method.
    get_properties()
        Read in the properties file passed into the constructor.

    """

    props_file = ""
    properties = None

    def __init__(self, props_file):
        """
        :param props_file:
            Fully qualified path to the properties file
        """
        self.props_file = props_file
        self.get_properties()

    def get_properties(self):
        """Read in the properties file passed into the constructor."""
        with open(self.props_file) as file:
            self.properties = yaml.safe_load(file)

    def run(self):
        """Iterates over the array of imported actions and calls each one's
        execute method.

        Method executes in its own thread.
        """
        pass
