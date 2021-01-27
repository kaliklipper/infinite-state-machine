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
import errno
import os
import time
import yaml

# Local application imports
from ism_exceptions.exceptions import RDBMSNotRecognised, TimestampFormatNotRecognised


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

    dao = None
    props_file = ""
    properties = None
    run_root = None
    run_timestamp = None

    def __init__(self, props_file, tag='default'):
        """
        :param props_file:
            Fully qualified path to the properties file
        """
        self.props_file = props_file
        self.tag = tag
        self.__get_properties()
        self.run_timestamp = self.__create_run_timestamp()
        self.__create_runtime_environment()
        self.__create_db(self.properties['database']['rdbms'])

    # Private methods
    def __create_run_timestamp(self):
        """Create a timestamp for the runtime directories in correct format

        Properties file runtime:stamp_format may be -
            epoch_milliseconds
            epoch_seconds
        """
        time_format = self.properties['runtime']['stamp_format']
        try:
            return {
                'epoch_seconds': int(time.time()),
                'epoch_milliseconds': int(time.time()*1000.0)
            }[time_format]
        except KeyError:
            raise TimestampFormatNotRecognised(f'Timestamp format ({time_format}) not recognised')

    def __create_runtime_environment(self):
        """Create the runtime environment

        The ISM will create a directory structure for the run. This will
        hold the database, runtime files and directories.
        """
        try:
            self.run_root = f'{self.properties["runtime"]["root_dir"]}' \
                   f'{os.path.sep}' \
                   f'{self.tag}' \
                   f'{os.path.sep}' \
                   f'{self.run_timestamp}'
            os.makedirs(self.run_root)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def __create_db(self, rdbms):
        """Route through to the correct RDBMS handler"""
        try:
            {
                'sqlite3': self.__sqlite3,
                'mysql': self.__mysql
            }[rdbms]()
        except KeyError:
            raise RDBMSNotRecognised(f'RDBMS {rdbms} not recognised / supported')

    def __get_properties(self):
        """Read in the properties file passed into the constructor."""
        with open(self.props_file) as file:
            self.properties = yaml.safe_load(file)

    def __mysql(self):
        pass

    def __sqlite3(self):
        """RDBMS set to SQLITE3

        Create the SQLITE3 database object and record the path to it.
        """
        from ism_dal.sqlite3_dao import Sqlite3

        db_dir = f'{self.run_root}{os.path.sep}database'
        db_path = f'{db_dir}{os.path.sep}{self.properties["database"]["db_name"]}'
        os.makedirs(db_dir)
        self.dao = Sqlite3()
        self.dao.create_database(db_path)

    # Public methods
    def run(self):
        """Iterates over the array of imported actions and calls each one's
        execute method.

        Method executes in its own thread.
        """
        pass
