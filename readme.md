# CodeforcesCrawler

## requirements

- python3
  - pyquery
  - mysql.connector

If you construct additional database, followings are required.

- numpy
- matplotlib
- joblib

## environment

We check our scripts on Windows 10.

You have to set environment variables like below to allow our scripts to access the databases.
```
CF_DB_USER=<user name using databases(default: root)>
MYSQL_PASS=<password for connection(default: pass)>
CF_DB=<name of the database(default: testcf)>
```

Before constructing, you have to create the database and user.
For other configuration for connection, you can modify 'Connector.py'.


## Construct the basic database

```
python miningInformation.py
python miningSource.py
```

