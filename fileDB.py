from Database import Connector
from userDB import UserDB
# from problemDB import ProblemDB

class FileDB:
    table_name = 'FileTable'
    key = 'file_name'
    column = [
        'file_name',
        'user_name',
        'lang',
        'verdict',
        'timestamp',
        'prob_index',
        'contestId',
        'url'
    ]
    data_table = {
        'file_name': 'VARCHAR(50)',
        'user_name': 'VARCHAR(30)',
        'lang': 'VARCHAR(20)',
        'verdict': 'VARCHAR(20)',
        'timestamp': 'BIGINT UNSIGNED',
        'prob_index': 'VARCHAR(5)',
        'contestId': 'INT(10)',
        'url': 'VARCHAR(55)'
    }

    def __init__(self):
        self.con = Connector()

    def initTable(self):
        self.con.createTable(self.table_name, self.data_table, primary_key=self.key)

    def close(self):
        self.con.close()

    def addFile(self, insert_data):
        if not self.key in insert_data:
            print('Error: no primary key in insert_data')
            return
        data = {}
        for col in self.column:
            if col in insert_data:
                data[col] = insert_data[col]
        if self.con.existKey(self.table_name, self.key, insert_data[self.key]):
            self.con.update(data, self.table_name, {self.key: insert_data[self.key]})
        else:
            self.con.insert(data, self.table_name)

    def update(self, keyname, update_data):
        self.con.update(update_data, self.table_name, {self.key: keyname})

    def getFiles(self, where, limit=-1):
        return self.con.get(self.table_name, self.column, where, limit)


'''
def getProblemIndex(prob_db, filename, points):
    """
    prohibited to use
    (column points is droped)
    """
    name = filename.split('.')[-2]
    prob_id = int(name.split('_')[-1])
    prob = prob_db.getProblem({'contestId': prob_id, 'points': points})
    # print(prob)
    if prob is None:
        return '-'
    else:
        return prob['prob_index']


def updateProbIndex():
    """
    prohibited to use
    (column points is droped)
    """
    udb = UserDB()
    users = udb.getAllUser()
    udb.close()
    prob_db = ProblemDB()

    fdb = FileDB()
    for i, user in enumerate(users):
        if (i+1)%10 == 0:
            print(i+1)
        # print(user)
        files = fdb.getFiles({'user_name': user})
        # print(files)
        if len(files) == 0 or files[0]['points'] is None:
            continue
        for row in files:
            if  not row['prob_index'] is None or row['points'] is None:
                continue
            if row['points'] == 0:
                prob_index = '-'
            else:
                prob_index = getProblemIndex(prob_db, row['file_name'], row['points'])
            fdb.update(row['file_name'], {'prob_index': prob_index})

    fdb.close()
'''

def updateUrl():
    udb = UserDB()
    users = udb.getAllUser()
    udb.close()
    fdb = FileDB()
    for i, user in enumerate(users):
        if (i+1)%10 == 0:
            print(i+1)
            fdb.con.connector.commit()
        files = fdb.getFiles({'user_name': user})
        for row in files:
            name = row['file_name']
            contest_id = name.split('_')[-1].split('.')[0]
            run_id = name.split('_')[-2]
            if len(contest_id) <= 4 or row['url'] == '-':
                continue
            print(row)
            fdb.update(name, {'url': '-'})
    fdb.close()


def updateContestId():
    udb = UserDB()
    users = udb.getAllUser()
    udb.close()
    fdb = FileDB()
    for i, user in enumerate(users):
        if (i+1)%10 == 0:
            print(i+1)
        files = fdb.getFiles({'user_name': user})
        for row in files:
            name = row['file_name']
            contestId = name.split('_')[-1].split('.')[0]
            fdb.update(name, {'contestId': contestId})


def countSecondSubmissions():
    udb = UserDB()
    users = udb.getAllUser()
    udb.close()
    fdb = FileDB()
    counter = [0]*100
    all_ac = 0
    for i, user in enumerate(users):
        if (i+1)%100 == 0:
            print(i+1)
            fdb.con.commit()
        files = fdb.getFiles({'user_name': user})
        ac_count = {}
        for row in files:
            if row['verdict'] != 'OK' or row['contestId'] is None or  row['prob_index'] is None:
                continue
            all_ac += 1
            prob_id = str(row['contestId']) + row['prob_index']
            if not prob_id in ac_count:
                ac_count[prob_id] = 0
            ac_count[prob_id] += 1
        for c in ac_count.values():
            counter[c] += 1
    print(counter)
    print(all_ac)


if __name__ == '__main__':
    countSecondSubmissions()
