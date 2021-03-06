from database.Database import Database
from database.fileDB import FileDB


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
        'files',
        'acceptance_sample',
        'submission_in_sample',
        'solved_in_sample',
    ]
    data_table = {
        'user_name': 'VARCHAR(30)',
        'files': 'INT(4)',
        'acceptance_sample': 'DOUBLE',
        'submission_in_sample': 'INT(5)',
        'solved_in_sample': 'INT(4)',
    }

    def __init__(self):
        super().__init__(self.table_name, self.key, self.column, self.data_table)


def get_ac_count(submission_list):
    if len(submission_list) == 0:
        return 0
    ac_count = filter(lambda x: x['verdict'] == 'OK', submission_list)
    return len(list(ac_count))


def set_acceptance_sample():
    usdb = UserSubmissionDB()
    udb = UserDB()
    fdb = FileDB()

    for i, user in enumerate(udb.select()):
        submissions = fdb.select(where={'user_name': user['user_name']})
        ac_rate = get_ac_count(submissions) / len(submissions)
        usdb.insert({
            'acceptance_sample': ac_rate,
            usdb.key: user[usdb.key],
        })
        if (i + 1) % 100 == 0:
            usdb.commit()
            print('%d' % (i + 1))
    usdb.close()
    udb.close()
    fdb.close()


def set_submissions_and_solves():
    usdb = UserSubmissionDB()
    udb = UserDB()
    fdb = FileDB()

    for i, user in enumerate(udb.select()):
        submissions = list(fdb.select(where={'user_name': user['user_name']}))
        ac_size = get_ac_count(submissions)
        submission_size = len(submissions)
        usdb.insert({
            'acceptance_sample': ac_size / submission_size,
            'solved_in_sample': ac_size,
            'submission_in_sample': submission_size,
            usdb.key: user[usdb.key],
        })
        if (i + 1) % 100 == 0:
            usdb.commit()
            print('%d' % (i + 1))
    usdb.close()
    udb.close()
    fdb.close()


def check_rating_distribution():
    udb = UserDB()
    user_list = sorted(udb.select(), key=lambda x: -x['rating'])
    for i, user in enumerate(user_list):
        if (i + 1) % 200 == 0:
            print(user['rating'], i + 1)


if __name__ == '__main__':
    check_rating_distribution()
