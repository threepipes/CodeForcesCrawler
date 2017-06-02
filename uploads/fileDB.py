import os
import shutil
from datetime import timedelta
from Database import Database
from contestDB import ContestDB

class FileDB(Database):
    table_name = 'File'
    key = 'file_name'
    column = [
        'file_name',
        'submission_id',
        'user_name',
        'lang',
        'verdict',
        'timestamp',
        'problem_id',
        'competition_id',
        'url',
        'during_competition',
    ]
    data_table = {
        'file_name': 'VARCHAR(50)',
        'submission_id': 'INT(10)',
        'user_name': 'VARCHAR(30)',
        'lang': 'VARCHAR(20)',
        'verdict': 'VARCHAR(20)',
        'timestamp': 'DATETIME',
        'problem_id': 'VARCHAR(6)',
        'competition_id': 'INT(10)',
        'url': 'VARCHAR(55)',
        'during_competition': 'BOOLEAN',
    }

    def __init__(self):
        super().__init__(self.table_name, self.key, self.column, self.data_table)


def remove_files():
    fdb = FileDB()
    file_list = fdb.select(col=['file_name'])
    files = set()
    for filename in file_list:
        files.add(filename['file_name'])
    # cwd = os.getcwd()
    dirname = '../data/src/'
    # print(dirname)
    src_list = os.listdir(dirname)

    for data in src_list:
        if data in files:
            continue
        shutil.move(dirname+data, '../data/tmp')


def set_is_during_contest():
    fdb = FileDB()
    cdb = ContestDB()
    contest_list = cdb.select()
    contests = len(contest_list)

    for i, contest in enumerate(contest_list):
        print('start %d/%d' % (i + 1, contests))
        cid = contest['competition_id']
        start = contest['start_time']
        end = start + timedelta(seconds=contest['duration_time'])
        for file_data in fdb.select(where={'competition_id': cid}):
            filename = file_data['file_name']
            timestamp = file_data['timestamp']
            if timestamp is None:
                is_during = False
            else:
                is_during = start <= timestamp < end
            fdb.update(filename, {'during_competition': int(is_during)})
        fdb.commit()

    fdb.close()
    cdb.close()


if __name__ == '__main__':
    set_is_during_contest()
