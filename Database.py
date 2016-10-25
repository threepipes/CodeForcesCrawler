import mysql.connector as mc


class Connector:
    def __init__(self):
        self.connector = mc.connect(
            user='pycf',
            passwd='pycf',
            host='localhost',
            db='CFUsers',
            buffered=True)

        self.cur = self.connector.cursor()

    def show(self, table):
        self.cur.execute('')
        self.cur.execute('SELECT * FROM %s' % table)
        result = self.cur.fetchall()
        for row in result:
            print(row)

    def insert(self, data, table):
        """data must be dict {DATA_NAME=DATA}"""
        dataname = ''
        values = ''
        for (key, value) in data.items():
            dataname += key + ','
            values += value + ','

        statement = 'INSERT INTO %s (%s) VALUES (%s)' % (table, dataname[:-1], values[:-1])
        self.cur.execute(statement)

    def close(self):
        self.cur.close
        self.connector.close


class Database:
    user_data = ['user_name', 'rating', 'max_rating']

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
        self.con.insert(user, 'UserTable')

    def addFile(self, username, filename, lang, verdict):
        self.con.insert({'file_name': filename, 'user_name': username}, 'FileTable')

    def showUserTable(self):
        self.con.show('UserTable')

    def showFileTable(self):
        self.con.show('FileTable')
