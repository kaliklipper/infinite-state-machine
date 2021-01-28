# python_state_machine
An infinite state machine implemented in python

# Unit Tests
Run the unit tests from the package root using this syntax:

```python -m unittest -v test.test_ism.TestISM```

To clean down the unit test mysql databases created  log into mysql using the -s option to give clean result sets then:

```Bradleys-MBP:~ atkinsb$ mysql -u root -s
mysql> SELECT CONCAT('DROP DATABASE `', SCHEMA_NAME, '`;') FROM `information_schema`.`SCHEMATA` WHERE SCHEMA_NAME LIKE 'default_%';
CONCAT('DROP DATABASE `', SCHEMA_NAME, '`;')
DROP DATABASE `default_1611855489819`;
DROP DATABASE `default_1611855533770`;
DROP DATABASE `default_1611856233213`;
DROP DATABASE `default_1611856253150`;
DROP DATABASE `default_1611856264937`;
```
Then copy and paste the drop statements into the command line.
