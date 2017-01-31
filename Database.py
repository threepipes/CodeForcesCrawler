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
        res = []
        for row in result:
            mp = {}
            for key, value in zip(col, row):
                mp[key] = value
            res.append(mp)
        return res

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


class Database:
    user_data = ['user_name', 'rating', 'max_rating']
    user_table = 'UserTable'
    file_table = 'FileTable'
    sample_user_table = 'SampleUserTable'

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

    def addFile(self, username, filename, lang, verdict, timestamp, points):
        data = {
            'file_name': filename,
            'user_name': username,
            'lang': lang,
            'verdict': verdict,
            'timestamp': timestamp,
            'points': points
        }
        if self.con.existKey(self.file_table, 'file_name', filename):
            self.con.update(data, self.file_table, {'file_name': filename})
        else:
            self.con.insert(data, self.file_table)

    def addSampleUser(self, username, files):
        data = {'user_name': username, 'files': files}
        self.con.insert(data, self.sample_user_table)

    def getSampleUsers(self):
        return self.con.get(self.sample_user_table, ['user_name'])

    def hasNull(self, username, col):
        element = self.con.get(self.file_table, [col], {'user_name': username}, 1)
        return len(element)>0 and element[0][col] is None

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
            'verdict': 'VARCHAR(20)',
            'timestamp': 'BIGINT UNSIGNED',
            'points': 'INT(5)'
        }
        self.con.createTable('FileTable', filetable, primary_key='file_name')

    def createSampleTableIfNotExists(self):
        if self.con.existTable(self.sample_user_table):
            return False
        sampletable = {
            'user_name': 'VARCHAR(30)',
            'files': 'INT(4)'
        }
        self.con.createTable(self.sample_user_table, sampletable, primary_key='user_name')
        return True

    def getSampleFilenames(self):
        result = self.con.innerJoin(self.sample_user_table, self.file_table, ['file_name'], 'user_name')
        filenames = list(map(lambda x: x[0], result))
        return filenames


def outputACRate():
    con = Connector()
    table = 'usertable'
    userlist = con.get(table, ['user_name', 'rating'])
    filelist = con.get('filetable', ['user_name', 'verdict'])
    msac = {}
    msng = {}
    for f in filelist:
        user = f['user_name']
        if not user in msac:
            msac[user] = 0
            msng[user] = 0
        if f['verdict'] == 'OK':
            msac[user] += 1
        else:
            msng[user] += 1

    stat = []
    for user in userlist:
        name = user['user_name']
        data = ['"%s"' % user['user_name'], user['rating']]
        data.append(msac[name]+msng[name])
        data.append(msac[name])
        if data[2] > 0:
            data.append(data[3]/data[2])
        stat.append(data)
    with open('data_0112.csv', 'w') as f:
        f.write('username, rating, submitted(recent 6 month), ac, ac/all\n')
        for row in stat:
            f.write(','.join(map(str, row)) + '\n')

