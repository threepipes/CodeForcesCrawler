import mysql.connector as mc


# TODO use join with array
def mapToStr(data, separator=',', connector='='):
    result = ''
    for (key, value) in data.items():
        if type(value) is str:
            v = "'%s'" % value
        else:
            v = str(value)
        result += '%s%s%s%s' % (key, connector, v, separator)
    return result[:-1]


class Connector:
    def __init__(self):
        self.connector = mc.connect(
            user='pycf',
            passwd='pycf',
            host='localhost',
            db='CFUsers',
            buffered=True)

        self.cur = self.connector.cursor()

    def createDB(self, dbname, drop=False):
        if drop:
            self.cur.execute('DROP DATABASE IF EXISTS %s' % dbname)
            self.cur.execute('CREATE DATABASE %s' % dbname)
        else:
            self.cur.execute('CREATE DATABASE IF NOT EXISTS %s' % dbname)

    def createTable(self, tablename, data, primary_key=None, drop=False):
        tabledata = []
        for name, typename in data.items():
            tabledata.append(' %s %s' % (name, typename))
        if not primary_key is None:
            tabledata.append(' PRIMARY KEY(%s)' % primary_key)
        statement = ',\n'.join(tabledata)
        if drop:
            self.cur.execute('DROP TABLE IF EXISTS %s' % tablename)
            self.cur.execute('CREATE TABLE %s(\n%s\n)' % (tablename, statement))
        else:
            self.cur.execute('CREATE TABLE IF NOT EXISTS %s(\n%s\n)' % (tablename, statement))

    def show(self, table):
        self.connector.commit()
        self.cur.execute('SELECT * FROM %s' % table)
        result = self.cur.fetchall()
        for row in result:
            print(row)

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
        statement = 'SELECT COUNT(*) FROM %s'
        if not where is None:
            condition = []
            for (key, value) in where.items():
                condition.append("%s='%s'" % (key, value))
            statement += ' WHERE %s' % ' and '.join(condition)
        self.cur.execute(statement)
        return self.cur.fetchall()

    def close(self):
        self.connector.commit()
        self.cur.close()
        self.connector.close()


class Database:
    user_data = ['user_name', 'rating', 'max_rating']
    user_table = 'UserTable'
    file_table = 'FileTable'

    def __init__(self):
        self.con = Connector()

    def addUser(self, user):
        """
        user consists of
            {str user_name(key),
            int rating,
            int max_rating}
        """
        for key in self.user_data:
            if not key in user:
                print('Failed to add user. Lack of %d' % key)
                return False
        table_key = self.user_data[0]
        if self.con.existKey(self.user_table, table_key, user[table_key]):
            self.con.update(user, self.user_table, {table_key: user[table_key]})
        else:
            self.con.insert(user, self.user_table)

    def addFile(self, username, filename, lang, verdict):
        data = {'file_name': filename, 'user_name': username, 'lang': lang, 'verdict': verdict}
        if self.con.existKey(self.file_table, 'file_name', filename):
            self.con.update(data, self.file_table, {'file_name': filename})
        else:
            self.con.insert(data, self.file_table)

    def showUserTable(self):
        self.con.show(self.user_table)

    def showFileTable(self):
        self.con.show(self.file_table)

    def close(self):
        self.con.close()

    def initTables(self):
        usertable = {
            'user_name': 'VARCHAR(30)',
            'rating': 'INT(4)',
            'max_rating': 'INT(4)'
        }
        self.con.createTable('UserTable', usertable, primary_key='user_name')

        filetable = {
            'file_name': 'VARCHAR(50)',
            'user_name': 'VARCHAR(30)',
            'lang': 'VARCHAR(20)',
            'verdict': 'VARCHAR(20)'
        }
        self.con.createTable('FileTable', filetable, primary_key='file_name')
