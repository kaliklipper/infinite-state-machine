# python_state_machine
An Infinite State Machine implemented in python

Why "Infinite"?

Finite state machines are a great method fopr implementing event driven applications and operating systems. 
However, when implemented, they become fixed implementations of an application that do not easily lend themselves
to refactoring into another application.

The Infinite State Machine implemented here uses "Action Packs" that can be easily shared with other 
 State Machines. By abstracting the actions required to implement specific functions, such as a message queue or 
an automation framework, developing a state machine becomes as simple and familiar as writing a Python application that 
imports its functionality in packages.

# Unit Tests
Run the unit tests from the package root using this syntax:

```python3 -m unittest -v ism.tests.test_ism.TestISM```

To clean down the unit test mysql databases created  log into mysql using the -s option to give clean result sets then:

```
mysql> SELECT CONCAT('DROP DATABASE `', SCHEMA_NAME, '`;') FROM `information_schema`.`SCHEMATA` 
WHERE SCHEMA_NAME LIKE 'ism_default_%'; 

CONCAT('DROP DATABASE `', SCHEMA_NAME, '`;')
DROP DATABASE `ism_default_1611855489819`;
DROP DATABASE `ism_default_1611855533770`;
DROP DATABASE `ism_default_1611856233213`;
DROP DATABASE `ism_default_1611856253150`;
DROP DATABASE `ism_default_1611856264937`;
```
Then copy and paste the drop statements into the command line.
