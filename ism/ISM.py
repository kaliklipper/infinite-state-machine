"""
Module contains the state machine runner itself.

Implements the following functions:
    * __init__ - Constructor accepts path to properties file and
    then calls get_properties() to load the YAML.
    * get_properties - Read the properties file into the properties attribute.
    * run - Iterates over the array of imported ism_core_actions and calls each one's
        execute method.
"""

# Standard library imports
import errno
import importlib.resources as pkg_resources
import json
import logging
import os
import time
import yaml

# Local application imports
from ism.exceptions.exceptions import PropertyKeyNotRecognised, RDBMSNotRecognised, TimestampFormatNotRecognised


class ISM:
    """
    Implements an Infinite State Machine

    Attributes
    ----------
    props_file: str
        Fully qualified path to the properties file.

    Methods
    -------
    run()
        Iterates over the array of ism_core_actions and calls each one's
        execute method.
    get_properties()
        Read in the properties file passed into the constructor.

    """

    dao = None
    logger = None
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
        self.logger.info(f'Starting run using user tag ('
                         f'{self.properties["runtime"]["tag"]}) and system tag ('
                         f'{self.properties["runtime"]["run_timestamp"]})')
        self.__create_db(self.properties['database']['rdbms'])
        self.__create_core_schema()
        self.__insert_core_data()

    # Private methods
    def __create_core_schema(self):
        """Create the core schema

        ISM needs a basic core of tables to run. Import the schema from ism.core.schema.json.
        """

        from . import core
        with pkg_resources.open_text(core, 'schema.json') as schema:
            data = json.load(schema)
            for table in data[self.properties['database']['rdbms'].lower()]['tables']:
                self.dao.execute_sql_statement(table)

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

    def __create_mysql(self):
        """Create the Mysql database for the run."""

        from ism.dal.mysql_dao import MySqlDAO

        self.properties['database']['run_db'] = \
            f'{self.properties["database"]["db_name"]}_' \
            f'{self.properties["runtime"]["tag"]}_' \
            f'{self.properties["runtime"]["run_timestamp"]}'
        self.dao = MySqlDAO(self.properties)
        self.dao.create_database(self.properties)
        self.logger.info(f'Created MySql database {self.properties["database"]["run_db"]}')

    def __create_sqlite3(self):
        """RDBMS set to SQLITE3

        Create the SQLITE3 database object and record the path to it.
        """

        from ism.dal.sqlite3_dao import Sqlite3DAO

        db_dir = f'{self.properties["runtime"]["run_dir"]}{os.path.sep}database'
        self.properties['database']['db_path'] = \
            f'{db_dir}{os.path.sep}{self.properties["database"]["db_name"]}'
        os.makedirs(db_dir)
        self.dao = Sqlite3DAO(self.properties)
        self.dao.create_database(self.properties)
        self.logger.info(f'Created Sqlite3 database {self.properties["database"]["db_path"]}')

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
            }[time_format.lower()]
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
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def __enable_logging(self):
        """Configure the logging to write to a log file in the run root

        Used this guide to set up logging. It explains how to set up different loggers
        for each module and have them referenced in the log.
        https://docs.python.org/3/howto/logging-cookbook.html
        """

        try:
            log_dir = f'{self.properties["runtime"]["run_dir"]}' \
                      f'{os.path.sep}' \
                      f'log'
            os.makedirs(log_dir)

            self.properties["logging"]["file"] = \
                f'{log_dir}' \
                f'{os.path.sep}' \
                f'{self.properties["logging"]["file"]}'

            log_level = {
                'DEBUG': logging.DEBUG,
                'INFO': logging.INFO,
                'WARNING': logging.WARNING,
                'ERROR': logging.ERROR,
                'CRITICAL': logging.CRITICAL
            }[self.properties['logging']['level'].upper()]

        except KeyError:
            raise PropertyKeyNotRecognised()
        except Exception:
            raise

        self.logger = logging.getLogger('ism')
        self.logger.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh = logging.FileHandler(self.properties["logging"]["file"], 'w')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        # Suppress propagation to STDOUT
        self.logger.propagate = self.properties.get('logging', {}).get('propagate', False)

    def __get_properties(self):
        """Read in the properties file passed into the constructor."""
        logging.info(f'Reading in properties from file ({self.properties_file})')
        with open(self.properties_file) as file:
            return yaml.safe_load(file)

    def __insert_core_data(self):
        """Insert the run data for the core

        ISM needs a basic core of actions to run. Import the data from ism.core.data.json.
        """

        from . import core
        with pkg_resources.open_text(core, 'data.json') as data:
            inserts = json.load(data)
            for insert in inserts[self.properties['database']['rdbms'].lower()]['inserts']:
                self.dao.execute_sql_statement(insert)

    # Public methods
    def get_database_name(self):
        """Return the path to the database if set"""

        db = {
                'sqlite3': self.properties.get('database', {}).get('db_path', None),
                'mysql': self.properties.get('database', {}).get("run_db", None)
            }[self.properties['database']['rdbms'].lower()]
        return db

    def get_tag(self):
        """Return the user tag for the runtime directories"""
        return self.properties['runtime']['tag']

    def set_tag(self, tag):
        """Set the user tag for the runtime directories"""
        self.properties['runtime']['tag'] = tag

    def run(self):
        """Iterates over the array of imported ism_core_actions and calls each one's
        execute method.

        Method executes in its own thread.
        """
        pass
