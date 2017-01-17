import Database as db
import requests as req
import json

base_url = 'http://codeforces.com/'
url = base_url + 'api/'

class ContestDB:
    table_name = 'ContestTable'

    def __init__(self):
        self.con = db.Connector()

    def initTables(self, drop_table=False):
        prob_table = {
            'contestId': 'INT(4)',
            'name': 'VARCHAR(200)',
            'start_time': 'INT(10)',
            'division': 'INT(2)'
        }
        self.con.createTable(self.table_name, prob_table, primary_key='contestId', drop=drop_table)

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
            'division': div,
        }
        self.con.insert(data, self.table_name)

    def close(self):
        self.con.close()


def getData(api):
    request = req.get(url+api)
    return request.json()


if __name__ == '__main__':
    db = ContestDB()
    db.initTables(True)
    print('fin set db')
    data = getData('contest.list')
    print('fin get data')
    for d in data['result']:
        db.addContest(d)
    db.close()
