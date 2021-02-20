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
import importlib.util
import inspect
import json
import logging
import os
import threading
import time
import yaml

# Local application imports
from ism.exceptions.exceptions import PropertyKeyNotRecognised, RDBMSNotRecognised, TimestampFormatNotRecognised, \
    ExecutionPhaseNotFound, MalformedActionPack
from . import core
from .core.base_action import BaseAction
from .core.action_normal_shutdown import ActionNormalShutdown
from .core.action_emergency_shutdown import ActionEmergencyShutdown
from .core.action_process_inbound_messages import ActionProcessInboundMessages
from .core.action_confirm_ready_to_run import ActionConfirmReadyToRun


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
        self.properties['running'] = False
        self.ism_thread = None
        self.actions = []
        self.__create_runtime_environment()
        self.__enable_logging()
        self.logger.info(f'Starting run using user tag ('
                         f'{self.properties["runtime"]["tag"]}) and system tag ('
                         f'{self.properties["runtime"]["run_timestamp"]})')
        self.__create_db(self.properties['database']['rdbms'])
        self.__create_core_schema()
        self.__insert_core_data()
        self.__import_core_actions()

    # Private methods
    def __create_core_schema(self):
        """Create the core schema

        ISM needs a basic core of tables to run. Import the schema from ism.core.schema.json.
        """

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
        tag_format = self.properties['runtime']['sys_tag_format']
        try:
            return {
                'epoch_seconds': int(time.time()),
                'epoch_milliseconds': int(time.time()*1000.0)
            }[tag_format.lower()]
        except KeyError:
            raise TimestampFormatNotRecognised(f'System tag format ({tag_format}) not recognised')

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

    def __get_properties(self) -> dict:
        """Read in the properties file passed into the constructor."""
        logging.info(f'Reading in properties from file ({self.properties_file})')
        with open(self.properties_file) as file:
            return yaml.safe_load(file)

    def __import_core_actions(self):
        """Import the core actions for the ISM"""

        args = {
            "dao": self.dao,
            "properties": self.properties
        }
        self.actions.append(ActionProcessInboundMessages(args))
        self.actions.append(ActionConfirmReadyToRun(args))
        self.actions.append(ActionEmergencyShutdown(args))
        self.actions.append(ActionNormalShutdown(args))

    def __insert_core_data(self):
        """Insert the run data for the core

        ISM needs a basic core of actions to run. Import the data from ism.core.data.json.
        """

        with pkg_resources.open_text(core, 'data.json') as data:
            inserts = json.load(data)
            for insert in inserts[self.properties['database']['rdbms'].lower()]['inserts']:
                self.dao.execute_sql_statement(insert)

    def __run(self):
        """Iterates over the array of imported actions and calls each one's
        execute method.

        Method executes in its own thread.
        """

        self.properties['running'] = True
        index = 0
        while self.properties['running']:
            self.actions[index].execute()
            index += 1
            if index >= len(self.actions):
                index = 0

    # Public methods
    def get_database_name(self) -> str:
        """Return the database name"""

        db = {
                'sqlite3': self.__get_sqlite3_db_name,
                'mysql': self.__get_mysql_db_name
            }[self.properties['database']['rdbms'].lower()]()
        return db

    def get_tag(self) -> str:
        """Return the user tag for the runtime directories"""
        return self.properties['runtime']['tag']

    def import_action_pack(self, pack):
        """Import an action pack

        Application can pass in action packs to enable the ISM to express
        specific functionality. For an example of how to call this method,
        see the unit test in tests/test_ism.py (test_import_action_pack).

        Each action pack is a python package containing:
            * At least one action class inheriting from ism.core.BaseAction
            * A data.json file containing at least the insert statements for the
            action in the control DB.
            * Optionally a schema.json file contain the create statements for any
            tables the action needs in the control DB.

            The package should contain nothing else and no sub packages.
        """
        import pkgutil
        action_args = {
            "dao": self.dao,
            "properties": self.properties
        }

        try:
            # Import the package containing the actions
            package = importlib.import_module(pack)
            # Find each action module in the package
            for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):
                # Should not be any sub packages in there
                if ispkg:
                    raise MalformedActionPack(
                        f'Passed malformed action pack ({pack}). Unexpected sub packages {modname}'
                    )
                # Import the module containing the action
                module = importlib.import_module(f'{pack}.{importer.find_spec(modname).name}')
                # Get the name of the action class, instantiate it and add to the collection of actions
                for action in inspect.getmembers(module, inspect.isclass):
                    if action[0] == 'BaseAction':
                        continue
                    if 'Action' in action[0]:
                        cl_ = getattr(module, action[0])
                        self.actions.append(cl_(action_args))

            # Get the supporting DB file/s
            self.import_action_pack_tables(package)

        except ModuleNotFoundError as e:
            logging.error(f'Module/s not found for argument ({pack})')
            raise

    def import_action_pack_tables(self, package):
        """"An action will typically create some tables and insert standing data.

        If supporting schema file exists, then create the tables. A data.json
         file must exist with at least one insert for the actions table or the action
         execute method wil not be able to activate or deactivate..
        """

        inserts_found = False
        path = os.path.split(package.__file__)[0]
        for root, dirs, files in os.walk(path):
            if 'schema.json' in files:
                schema_file = os.path.join(root, 'schema.json')
                with open(schema_file) as tables:
                    data = json.load(tables)
                    for table in data[self.properties['database']['rdbms'].lower()]['tables']:
                        self.dao.execute_sql_statement(table)

            if 'data.json' in files:
                data = os.path.join(root, 'data.json')
                with open(data) as statements:
                    inserts = json.load(statements)
                    for insert in inserts[self.properties['database']['rdbms'].lower()]['inserts']:
                        self.dao.execute_sql_statement(insert)
                inserts_found = True

            if not inserts_found:
                raise MalformedActionPack(f'No insert statements found for action pack ({package})')

    def set_tag(self, tag):
        """Set the user tag for the runtime directories"""
        self.properties['runtime']['tag'] = tag

    def start(self, join=False):
        """Start running the state machine main loop in the background

        Caller has the option to run the thread as a daemon or to join() it.
        """

        self.logger.info('Starting run() thread')
        self.ism_thread = threading.Thread(target=self.__run, daemon=True)
        self.ism_thread.start()
        if join:
            self.ism_thread.join()

    def stop(self):
        """Stop the run in the background thread"""
        self.properties['running'] = False

    # Test Methods
    def __get_mysql_db_name(self) -> str:
        """Retrieve the MySql db name from the information schema."""

        sql = self.dao.prepare_parameterised_statement(
            'select SCHEMA_NAME from information_schema.schemata WHERE SCHEMA_NAME = ?'
        )
        params = (self.properties.get("database", {}).get("run_db", None),)
        rows = self.dao.execute_sql_query(sql, params)
        return ''.join(rows[0]) if rows else 'Not found'

    def __get_sqlite3_db_name(self) -> str:
        """Return the path to the Sqlite3 database."""

        return self.properties.get('database', {}).get('db_path', 'Not found')

    def get_execution_phase(self) -> str:
        """Get the current active execution phase.

        e.g.
            * RUNNING
            * STARTING
            * EMERGENCY_SHUTDOWN
            * NORMAL_SHUTDOWN
            * STOPPED
        """
        try:
            return self.dao.execute_sql_query(
                f'SELECT execution_phase FROM phases WHERE state = 1'
            )[0][0]
        except IndexError as e:
            raise ExecutionPhaseNotFound(f'Current execution_phase not found in control database. ({e})')
