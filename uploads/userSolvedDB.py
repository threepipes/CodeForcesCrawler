from fileDB import FileDB


class userSolvedDB(Database):
    table_name = 'ParticipantSolved'
    key = 'first_ac_file'
    column = [
        'first_ac_file',
        'user_name',
        'problem_id',
        'competition_id',
        'during_competition',
    ]
    data_table = {
        'first_ac_file': 'VARCHAR(50)',
        'user_name': 'VARCHAR(30)',
        'problem_id': 'VARCHAR(6)',
        'competition_id': 'INT(10)',
        'during_competition': 'BOOLEAN',
    }

    def __init__(self):
        super().__init__(self.table_name, self.key, self.column, self.data_table)


def create_usersolved_db():
    fdb = FileDB()
    