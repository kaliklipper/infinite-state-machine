"""The test support package implements actions that allow the unit test
harness to interact with the state machine's primary thread without causing
contention for resources like the Sqlite3 database.

This action creates the inbound and outbound directories for the test support actions.
Then activates the support actions.
"""

# Standard library imports
import os

# Local application imports
from ism.core.base_action import BaseAction


class ActionBeforeTestSupport(BaseAction):

    def execute(self):
        if self.active:

            try:
                inbound = self.properties['test']['support']['inbound']
                outbound = self.properties['test']['support']['outbound']
                archive = self.properties['test']['support']['archive']
            except KeyError as e:
                self.logger.error(f'Failed to read directory entries from properties file. KeyError ({e})')
                raise

            try:
                if not os.path.exists(inbound):
                    os.makedirs(inbound)
                if not os.path.exists(outbound):
                    os.makedirs(outbound)
                if not os.path.exists(archive):
                    os.makedirs(archive)
            except OSError as e:
                self.logger.error(f'Failed to create directory for test support actions. OSError ({e})')
                raise

            self.activate('ActionInboundMsg')
            self.activate('ActionOutboundMsg')
            self.deactivate()
