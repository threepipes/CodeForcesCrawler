from Database import Connector
from userDB import UserDB
from problemDB import ProblemDB

class FileDB:
    table_name = 'FileTable'

    def __init__(self):
        self.con = Connector()

    def initTable(self):
        filetable = {
            'file_name': 'VARCHAR(50)',
            'user_name': 'VARCHAR(30)',
            'lang': 'VARCHAR(20)',
            'verdict': 'VARCHAR(20)',
            'timestamp': 'BIGINT UNSIGNED',
            'points': 'INT(5)',
            'prob_index': 'VARCHAR(5)'
        }
        self.con.createTable('FileTable', filetable, primary_key='file_name')

    def close(self):
        self.con.close()

    def addFile(self, username, filename, lang, verdict, timestamp, points):
        data = {
            'file_name': filename,
            'user_name': username,
            'lang': lang,
            'verdict': verdict,
            'timestamp': timestamp,
            'points': points
        }
        if self.con.existKey(self.table_name, 'file_name', filename):
            self.con.update(data, self.table_name, {'file_name': filename})
        else:
            self.con.insert(data, self.table_name)

    def update(self, filename, update_data):
        # print(filename+' '+str(update_data))
        self.con.update(update_data, self.table_name, {'file_name': filename})

    def getFiles(self, where):
        cols = [
            'file_name',
            'user_name',
            'lang',
            'verdict',
            'timestamp',
            'points',
            'prob_index'
        ]
        return self.con.get(self.table_name, cols, where)


def getProblemIndex(prob_db, filename, points):
    name = filename.split('.')[-2]
    prob_id = int(name.split('_')[-1])
    prob = prob_db.getProblem({'contestId': prob_id, 'points': points})
    # print(prob)
    if prob is None:
        return '-'
    else:
        return prob['prob_index']


def updateProbIndex():
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

if __name__ == '__main__':
    updateProbIndex()
