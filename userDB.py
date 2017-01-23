from Database import Connector

class UserDB:
    table_name = 'UserTable'
    user_data = ['user_name', 'rating', 'max_rating']

    def __init__(self):
        self.con = Connector()

    def initTable(self):
        usertable = {
            'user_name': 'VARCHAR(30)',
            'rating': 'INT(4)',
            'max_rating': 'INT(4)'
        }
        self.con.createTable('UserTable', usertable, primary_key='user_name')

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
        if self.con.existKey(self.table_name, table_key, user[table_key]):
            self.con.update(user, self.table_name, {table_key: user[table_key]})
        else:
            self.con.insert(user, self.table_name)

    def getAllUser(self):
        users = self.con.get(self.table_name, ['user_name'])
        return [user['user_name'] for user in users]

    def getAllUserWithRating(self):
        return self.con.get(self.table_name, ['user_name', 'rating'])

    def close(self):
        self.con.close()