from database.Database import Database
from database.fileDB import FileDB
from database.problemDB import ProblemDB


class UserSolvedDB(Database):
    table_name = 'ParticipantSolved'
    key = 'first_ac_file'
    column = [
        'first_ac_file',
        'user_name',
        'problem_id',
        'during_competition',
    ]
    data_table = {
        'first_ac_file': 'VARCHAR(50)',
        'user_name': 'VARCHAR(30)',
        'problem_id': 'VARCHAR(6)',
        'during_competition': 'BOOLEAN',
    }

    def __init__(self):
        super().__init__(self.table_name, self.key, self.column, self.data_table)


def create_usersolved_db():
    usdb = UserSolvedDB()
    usdb.init_table()
    fdb = FileDB()
    pdb = ProblemDB()

    for prob in pdb.select():
        prob_id = prob['problem_id']
        used = set()
        print(prob_id)
        for file_data in fdb.select(where={'problem_id': prob_id}):
            user_name = file_data['user_name']
            if user_name in used:
                continue
            used.add(user_name)
            update_data = {
                'first_ac_file': file_data['file_name'],
                'user_name': user_name,
                'problem_id': prob_id,
                'during_competition': file_data['during_competition']
            }
            usdb.insert(update_data)
        usdb.commit()

    usdb.close()
    fdb.close()
    pdb.close()


if __name__ == '__main__':
    create_usersolved_db()
