from Database import Database
import os
import shutil

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
        'url'
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
        'url': 'VARCHAR(55)'
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

if __name__ == '__main__':
    remove_files()
