"""Custom Exceptions for the state machine"""


class RDBMSNotRecognised(Exception):

    def __init__(self, message='RDBMS not recognised / supported'):
        self.message = message
        super().__init__(self.message)


class TimestampFormatNotRecognised(Exception):

    def __init__(self, message='Timestamp format not recognised'):
        self.message = message
        super().__init__(self.message)
