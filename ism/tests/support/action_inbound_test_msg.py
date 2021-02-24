"""The test support package implements actions that allow the unit test
harness to interact with the state machine's primary thread without causing
contention for resources like the Sqlite3 database.

This action checks the inbound directory for message files and reads the content
into the database table test_support_messages_inbound. Going on to update the action table
if appropriate.

Messages arrive as:
    inbound/file_name.json
    inbound/file_name.smp

.json being the message file and .smp being the semaphore file.

Message format is:
{
    sender_id: integer
    action: "NameOfAction",
    payload: {JSON Object}
}
"""

# Standard library imports
import os
import json

# Local application imports
from ism.core.base_action import BaseAction
from ism.exceptions.exceptions import OrphanedSemaphoreFile


class ActionInboundTestMsg(BaseAction):

    def execute(self):
        if self.active:
            inbound_dir = self.properties['test']['support']['inbound']
            archive_dir = self.properties['test']['support']['archive']

            # Pick up any semaphore files in the inbound directory
            for file in [fn for fn in os.listdir(inbound_dir) if fn.endswith('.smp')]:
                # Semaphore file should have an associated msg file of same name
                temp = os.path.splitext(file)
                file_name = temp[0]
                msg_file = f'{inbound_dir}{os.path.sep}{file_name}.json'
                if not os.path.exists(msg_file):
                    raise OrphanedSemaphoreFile(f'Semaphore file ({file}) without associated message file.')

                # Message file found so read it into the DB test messages table
                with open(msg_file, 'r') as message_file:
                    message = json.loads(message_file.read())
                    sql = self.dao.prepare_parameterised_statement(
                        'INSERT INTO test_support_messages_inbound (action, payload) VALUES(?, ?)'
                    )
                    self.dao.execute_sql_statement(
                            sql,
                            (
                                message['action'],
                                json.dumps(message['payload'])
                            )
                       )

                # Archive the file so we don't process it again
                destination = f'{archive_dir}{os.path.sep}{file_name}.json'
                os.rename(msg_file, destination)
                destination = f'{archive_dir}{os.path.sep}{file_name}.smp'
                os.rename(f'{inbound_dir}{os.path.sep}{file_name}.smp', destination)

                # Update the test action's payload
                sql = self.dao.prepare_parameterised_statement(
                    'UPDATE actions SET payload = ? WHERE action = ?'
                )
                self.dao.execute_sql_statement(
                    sql,
                    (
                        json.dumps(message['payload']),
                        message['action']
                    )
                )
                # Enable the test action
                self.activate(message['action'])
