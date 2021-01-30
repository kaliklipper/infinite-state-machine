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
import logging
import os
import time
import yaml

# Local application imports
from ism_exceptions.exceptions import LogLevelNotRecognised, RDBMSNotRecognised, TimestampFormatNotRecognised


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
    properties_file = None
    properties = None

    def __init__(self, *args):
        """
        :param props_file:
            Fully qualified path to the properties file
        """
        self.properties_file = args[0]['properties_file']
        self.properties = self.__get_properties()
        self.properties['database']['password'] = args[0].get('database', {}).get('password', None)
        self.properties['database']['db_path'] = None
        self.properties['runtime']['run_timestamp'] = self.__create_run_timestamp()
        self.properties['runtime']['tag'] = args[0].get('tag', 'default')
        self.__create_runtime_environment()
        self.__enable_logging()
        logging.info(f'Starting run using user tag ('
                     f'{self.properties["runtime"]["tag"]}) and system tag ('
                     f'{self.properties["runtime"]["run_timestamp"]})')
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
            self.properties["runtime"]["run_dir"] = f'{self.properties["runtime"]["root_dir"]}' \
                   f'{os.path.sep}' \
                   f'{self.properties["runtime"]["tag"]}' \
                   f'{os.path.sep}' \
                   f'{self.properties["runtime"]["run_timestamp"]}'
            os.makedirs(self.properties["runtime"]["run_dir"])
            logging.info(f'Created runtime directory at {self.properties["runtime"]["run_dir"]}')
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def __create_db(self, rdbms):
        """Route through to the correct RDBMS handler"""
        try:
            {
                'sqlite3': self.__create_sqlite3,
                'mysql': self.__create_mysql
            }[rdbms.lower()]()
        except KeyError:
            raise RDBMSNotRecognised(f'RDBMS {rdbms} not recognised / supported')
        except Exception:
            raise

    def __enable_logging(self):
        """Configure the logging to write to a log file in the run root"""
        try:
            log_dir = f'{self.properties["runtime"]["run_dir"]}' \
                      f'{os.path.sep}' \
                      f'log'
            os.makedirs(log_dir)

            self.properties["logging"]["file"] = \
                f'{log_dir}' \
                f'{os.path.sep}' \
                f'{self.properties["logging"]["file"]}'

            logging.basicConfig(
                filename=self.properties["logging"]["file"],
                filemode='w',
                level={
                    'DEBUG': logging.DEBUG,
                    'INFO': logging.INFO,
                    'WARNING': logging.WARNING,
                    'ERROR': logging.ERROR,
                    'CRITICAL': logging.CRITICAL
                }[self.properties['logging']['level'].upper()],
                format='%(asctime)s %(message)s'
            )
        except KeyError:
            raise LogLevelNotRecognised(f'RDBMS {self.properties["logging"]["level"]} not recognised / supported')
        except Exception:
            raise

    def __get_properties(self):
        """Read in the properties file passed into the constructor."""
        logging.info(f'Reading in properties from file ({self.properties_file})')
        with open(self.properties_file) as file:
            return yaml.safe_load(file)

    def __create_mysql(self):

        from ism_dal.mysql_dao import MySqlDAO
        self.dao = MySqlDAO()
        self.properties['database']['run_db'] = \
            f'{self.properties["runtime"]["tag"]}_' \
            f'{self.properties["runtime"]["run_timestamp"]}'
        self.dao.create_database(self.properties)
        logging.info(f'Created MySql database {self.properties["database"]["run_db"]}')

    def __create_sqlite3(self):
        """RDBMS set to SQLITE3

        Create the SQLITE3 database object and record the path to it.
        """
        from ism_dal.sqlite3_dao import Sqlite3DAO

        db_dir = f'{self.properties["runtime"]["run_dir"]}{os.path.sep}database'
        self.properties['database']['db_path'] = \
            f'{db_dir}{os.path.sep}{self.properties["database"]["db_name"]}'
        os.makedirs(db_dir)
        self.dao = Sqlite3DAO()
        self.dao.create_database(self.properties)
        logging.info(f'Created Sqlite3 database {self.properties["database"]["db_path"]}')

    # Public methods
    def get_database_name(self):
        """Return the path to the database if set"""

        db = {
                'sqlite3': self.properties['database']['db_path'],
                'mysql': self.properties['database']["run_db"]
            }[self.properties['database']['rdbms'].lower()]
        return db

    def get_tag(self):
        """Return the user tag for the runtime directories"""
        return self.properties['runtime']['tag']

    def set_tag(self, tag):
        """Set the user tag for the runtime directories"""
        self.properties['runtime']['tag'] = tag

    def run(self):
        """Iterates over the array of imported actions and calls each one's
        execute method.

        Method executes in its own thread.
        """
        pass

