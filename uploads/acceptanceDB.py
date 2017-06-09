import os
from Database import Database
import csv

class AcceptanceDB(Database):
    table_name = 'Acceptance'
    key = 'problem_id'
    column = [
        'problem_id',
        'submission_in_sample',
        'solved_in_sample',
        'submission',
        'solved',
        'acceptance_rate',
        'lastmodified'
    ]
    data_table = {
        'problem_id': 'VARCHAR(20)',
        'submission_in_sample': 'INT(6)',
        'solved_in_sample': 'INT(5)',
        'submission': 'INT(6)',
        'solved': 'INT(5)',
        'acceptance_rate': 'DOUBLE',
        'lastmodified': 'DATE'
    }

    def __init__(self):
        super(AcceptanceDB, self).__init__(self.table_name, self.key, self.column, self.data_table)


def fix_rate():
    adb = AcceptanceDB()
    for row in adb.select():
        pid = row['problem_id']
        solved = row['solved']
        submission = row['submission']
        ac_rate = min(1, solved / submission)
        adb.update(pid, {
            'acceptance_rate': ac_rate
        })
    adb.commit()


def distribution_plot():
    path = './problem_info/'
    if not os.path.exists(path):
        os.mkdir(path)
    file_name = 'acceptance_rate_distribution.png'
    db = AcceptanceDB()
    data = []
    for prob in db.select():
        data.append(prob['acceptance_rate'])

    from matplotlib import pyplot as plt

    plt.figure(figsize=(20, 8))
    plt.hist(data, bins=20)
    plt.savefig(path + file_name)
    plt.close()


if __name__ == '__main__':
    distribution_plot()
