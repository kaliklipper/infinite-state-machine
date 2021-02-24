"""The test support package implements actions that allow the unit test
harness to interact with the state machine's primary thread without causing
contention for resources like the Sqlite3 database.

This action checks the outbound table in the database for messages and writes them to file.
"""

# Standard library imports
import json
import os

# Local application imports
from ism.core.base_action import BaseAction


class ActionOutboundTestMsg(BaseAction):

    def execute(self):

        if self.active():

            # Have an outbound message to send so get it from the DB
            payload = json.loads(self.get_payload()[0][0])

            # Write it to file in the outbound directory
            out_dir = self.properties.get('test', {}).get('support', {}).get('outbound', None)
            path = f'{out_dir}{os.path.sep}{payload["sender_id"]}.json'
            with open(path, 'w') as file:
                file.write(json.dumps(payload))

            # Clear the payload for completeness
            self.clear_payload()

            self.deactivate()
