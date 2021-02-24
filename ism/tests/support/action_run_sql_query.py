"""Run a SQL query on behalf of a unit test.

Give the result to ActionOutboundTestMessage as its payload.
"""

# Standard library imports
import json

# Local application imports
from ism.core.base_action import BaseAction


class ActionRunSqlQuery(BaseAction):

    def execute(self):

        if self.active():

            # Get the sql from the payload for this action
            this_payload = json.loads(self.get_payload()[0][0])

            # Execute the sql query
            try:
                result = self.dao.execute_sql_query(this_payload['sql'])
            except KeyError as err:
                self.logger.error(f'sql key not found in payload for test action ActionRunSqlQuery ({err})')

            # Now need to send the results back as an outbound test message
            outbound_payload = {"query_result": result, "sender_id": this_payload['sender_id']}
            sql = self.dao.prepare_parameterised_statement(
                'UPDATE actions SET payload = ? WHERE action = ?'
            )
            self.dao.execute_sql_statement(
                sql,
                (
                    json.dumps(outbound_payload),
                    'ActionOutboundTestMsg'
                )
            )

            # Enable the test action
            self.activate('ActionOutboundTestMsg')

            # Finished so deactivate this action
            self.clear_payload()
            self.deactivate()
