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
    csv_path = 'C:/Work/Python/Lab/CodeForcesCrawler/data/fix/ac_rate.csv'
    data = []
    with open(csv_path) as f:
        for line in csv.reader(f):
            data.append(line)
    data = data[1:]
    adb = AcceptanceDB()
    for row in data:
        pid = row[1]
        solved = row[2]
        submission = row[3]
        ac_rate = row[4]
        adb.update(pid, {
            'solved': solved,
            'submission': submission,
            'acceptance_rate': ac_rate
        })
    adb.commit()


def distribution_plot():
    path = './problem_info/'
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
