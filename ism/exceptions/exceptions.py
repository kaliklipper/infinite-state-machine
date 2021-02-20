"""Custom Exceptions for the state machine"""


class ActivationOutOfPhase(Exception):

    def __init(self, message='Attempt to activate action out of correct phase'):
        self.message = message
        super().__init__(self.message)


class DuplicateDataInControlDatabase(Exception):

    def __init(self, message='Duplicate records found in control database'):
        self.message = message
        super().__init__(self.message)


class ExecutionPhaseNotFound(Exception):

    def __init(self, message='Current execution_phase not found in control database'):
        self.message = message
        super().__init__(self.message)


class ExecutionPhaseUnrecognised(Exception):

    def __init(self, message='Passed unrecognised execution_phase'):
        self.message = message
        super().__init__(self.message)


class MalformedActionPack(Exception):

    def __init(self, message='Passed malformed action pack for import.'):
        self.message = message
        super().__init__(self.message)


class MissingDataInControlDatabase(Exception):

    def __init(self, message='Record not found in control database'):
        self.message = message
        super().__init__(self.message)


class PropertyKeyNotRecognised(Exception):

    def __init__(self, message='Property Key not recognised'):
        self.message = message
        super().__init__(self.message)


class RDBMSNotRecognised(Exception):

    def __init__(self, message='RDBMS not recognised / supported'):
        self.message = message
        super().__init__(self.message)


class TimestampFormatNotRecognised(Exception):

    def __init__(self, message='Timestamp format not recognised'):
        self.message = message
        super().__init__(self.message)


class UnrecognisedParameterisationCharacter(Exception):

    def __init__(self, message='Parameterisation character not recognised / found'):
        self.message = message
        super().__init__(self.message)
