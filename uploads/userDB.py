from Connector import Connector
from Database import Database

class UserDB(Database):
    table_name = 'Participant'
    key = 'user_name'
    column = [
        'user_name',
        'rating',
        'max_rating'
    ]
    data_table = {
        'user_name': 'VARCHAR(30)',
        'rating': 'INT(4)',
        'max_rating': 'INT(4)'
    }

    def __init__(self):
        super().__init__(self.table_name, self.key, self.column, self.data_table)


class UserSubmissionDB(Database):
    table_name = 'ParticipantSubmission'
    key = 'user_name'
    column = [
        'user_name',
        'files'
    ]
    data_table = {
        'user_name': 'VARCHAR(30)',
        'files': 'INT(4)'
    }

    def __init__(self):
        super().__init__(self.table_name, self.key, self.column, self.data_table)
