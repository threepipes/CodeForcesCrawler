import os
import mysql.connector as mc


def mapToStr(data, separator=',', connector='='):
    result = []
    for (key, value) in data.items():
        if type(value) is str:
            v = "'%s'" % value
        else:
            v = str(value)
        result.append('%s%s%s' % (key, connector, v))
    return separator.join(result)


class Connector:
    def __init__(self):
        self.connector = mc.connect(
            user=os.getenv('CF_DB_USER', 'root'),
            passwd=os.getenv('MYSQL_PASS', 'pass'),
            host='localhost',
            db=os.getenv('CF_DB', 'testcf'),
            buffered=True)

        self.cur = self.connector.cursor()

    def createDB(self, dbname, drop=False):
        if drop:
            self.cur.execute('DROP DATABASE IF EXISTS %s' % dbname)
            self.cur.execute('CREATE DATABASE %s' % dbname)
        else:
            self.cur.execute('CREATE DATABASE IF NOT EXISTS %s' % dbname)
    
    def dropTable(self, tablename):
        self.cur.execute('DROP TABLE IF EXISTS %s' % tablename)

    def createTable(self, tablename, data, primary_key=None, foreign_key=None, drop=False):
        tabledata = []
        for name, typename in data.items():
            tabledata.append(' %s %s' % (name, typename))
        if not primary_key is None:
            tabledata.append(' PRIMARY KEY(%s)' % primary_key)
        if not foreign_key is None:
            cascade = 'ON DELETE CASCADE ON UPDATE CASCADE'
            for key, table in foreign_key.items():
                tabledata.append(' FOREIGN KEY(%s) REFERENCES %s(%s) %s' % (key, table, key, cascade))
        statement = ',\n'.join(tabledata)
        def_charset = 'DEFAULT CHARSET=utf8mb4'
        if drop:
            self.cur.execute('DROP TABLE IF EXISTS %s' % tablename)
            self.cur.execute('CREATE TABLE %s(\n%s\n)%s' % (tablename, statement, def_charset))
        else:
            self.cur.execute('CREATE TABLE IF NOT EXISTS %s(\n%s\n)%s' % (tablename, statement, def_charset))

    def show(self, table):
        self.connector.commit()
        self.cur.execute('SELECT * FROM %s' % table)
        result = self.cur.fetchall()
        for row in result:
            print(row)

    def innerJoin(self, table_base, table_into, col, join_key):
        cols = ','.join(col)
        strs = (cols, table_base, table_into, table_base, join_key, table_into, join_key)
        statement = 'SELECT %s FROM %s INNER JOIN %s ON %s.%s = %s.%s' % strs
        self.cur.execute(statement)
        return self.cur.fetchall()

    def get(self, table, col, where=None, limit=-1):
        self.connector.commit()
        where_sentence = ''
        limit_sentence = ''
        if limit > 0:
            limit_sentence = ' LIMIT ' + str(limit)
        if not where is None:
            if isinstance(where, dict):
                where_sentence = ' WHERE ' + mapToStr(where, separator=' and ')
            elif isinstance(where, list):
                where_sentence = ' WHERE ' + ' and '.join(where)
            elif isinstance(where, str):
                where_sentence = ' WHERE ' + where
        sentence = 'SELECT %s FROM %s%s%s' % (','.join(col), table, where_sentence, limit_sentence)
        self.cur.execute(sentence)
        result = self.cur.fetchall()
        # res = []
        for row in result:
            mp = {}
            for key, value in zip(col, row):
                mp[key] = value
            # res.append(mp)
            yield mp
        # return res

    def insert(self, data, table, update=False):
        """data must be dict {DATA_NAME=DATA}"""
        dataname = ','.join(data.keys())
        values = tuple(data.values())
        holder = ','.join(['%s']*len(values))

        statement = 'INSERT INTO %s (%s) VALUES (%s)' % (table, dataname, holder)
        if update:
            statement += ' ON DUPLICATE KEY UPDATE'
        self.cur.execute(statement, values)

    def update(self, data, table, key):
        changes = mapToStr(data)
        select_key = mapToStr(key)
        statement = 'UPDATE %s SET %s WHERE %s' % (table, changes, select_key)
        self.cur.execute(statement)

    def existKey(self, table, key_name, value):
        self.connector.commit()
        statement = 'SELECT %s FROM %s WHERE %s=%%s' % (key_name, table, key_name)
        self.cur.execute(statement, (value,))
        result = self.cur.fetchall()
        return len(result) > 0

    def count(self, table, where=None):
        self.connector.commit()
        statement = 'SELECT COUNT(*) FROM ' + table
        if not where is None:
            condition = []
            for (key, value) in where.items():
                condition.append("%s='%s'" % (key, value))
            statement += ' WHERE %s' % ' and '.join(condition)
        self.cur.execute(statement)
        return self.cur.fetchall()[0][0]

    def close(self):
        self.connector.commit()
        self.cur.close()
        self.connector.close()

    def existTable(self, table):
        self.cur.execute('SHOW TABLES')
        tables = self.cur.fetchall()
        return (table,) in tables

    def commit(self):
        self.connector.commit()
