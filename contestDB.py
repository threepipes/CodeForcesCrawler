import Database as db
import requests as req
import json
from SleepTimer import SleepTimer

base_url = 'http://codeforces.com/'
url = base_url + 'api/'

class ContestDB:
    table_name = 'ContestTable'
    column = [
        'contestId',
        'name',
        'start_time',
        'duration_time',
        'division',
        'contestant'
    ]
    key = 'contestId'

    def __init__(self):
        self.con = db.Connector()

    def initTables(self, drop_table=False):
        prob_table = {
            'contestId': 'INT(4)',
            'name': 'VARCHAR(200)',
            'start_time': 'INT(10)',
            'duration_time': 'INT(10)',
            'division': 'INT(2)',
            'contestant': 'INT(6)'
        }
        self.con.createTable(self.table_name, prob_table, primary_key=self.key, drop=drop_table)

    def addContest(self, data_json):
        start_time = 0
        if 'startTimeSeconds' in data_json:
            start_time = data_json['startTimeSeconds']
        name = data_json['name']
        div = -1
        if 'Div. 1' in name and 'Div. 2' in name:
            div = -1
        elif 'Final' in name:
            div = 0
        elif 'Div. 1' in name:
            div = 1
        elif 'Div. 2' in name:
            div = 2

        data = {
            'contestId': data_json['id'],
            'name': name,
            'start_time': start_time,
            'duration_time': data_json['durationSeconds'],
            'division': div,
        }
        self.con.insert(data, self.table_name)

    def updateContest(self, update_data):
        self.con.update(update_data, self.table_name, {self.key: update_data[self.key]})

    def getContests(self):
        return self.con.get(self.table_name, self.column)

    def close(self):
        self.con.close()


timer = SleepTimer()
def getData(api, where=None):
    timer.sleep(0.4)
    request = req.get(url+api, params=where)
    timer.reset()
    return request.json()


def setContestants():
    db = ContestDB()
    contests = db.getContests()
    cid_name = 'contestId'
    for i, con in enumerate(contests[680:]):
        print('%d/%d' % (i+1, len(contests)))
        success = True
        while True:
            try:
                data = getData('contest.ratingChanges', {cid_name: con[cid_name]})
                if data['status'] == 'OK':
                    break
                else:
                    data = getData('contest.standings', {cid_name: con[cid_name], 'showUnofficial': 'true'})
                    if data['status'] == 'OK':
                        break
                    else:
                        print('cannot get data:'+str(con))
                        success = False
                        break
            except:
                print('error:')
            timer.sleep(5)
        if not success:
            continue
        num = len(data['result'])
        update = {cid_name: con[cid_name], 'contestant': num}
        db.updateContest(update)
    db.close()


if __name__ == '__main__':
    setContestants()
