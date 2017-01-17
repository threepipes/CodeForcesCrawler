import Database as db
import requests as req
import json

base_url = 'http://codeforces.com/'
url = base_url + 'api/'

class ProblemDB:
    table_name = 'ProblemTable'

    def __init__(self):
        self.con = db.Connector()

    def initTable(self, drop_table=False):
        prob_table = {
            'id': 'VARCHAR(20)',
            'contestId': 'INT(10)',
            'prob_index': 'VARCHAR(5)',
            'points': 'INT(5)',
        }
        self.con.createTable(self.table_name, prob_table, primary_key='id', drop=drop_table)

    def addProblem(self, prob_json):
        points = 0
        if 'points' in prob_json:
            points = int(prob_json['points'])
        data = {
            'id': str(prob_json['contestId']) + prob_json['index'],
            'contestId': prob_json['contestId'],
            'prob_index': prob_json['index'],
            'points': points,
        }
        self.con.insert(data, self.table_name)

    def getProblem(self, where):
        cols = [
            'id', 'contestId', 'prob_index', 'points'
        ]
        ret = self.con.get(self.table_name, cols, where)
        if len(ret) == 0:
            return None
        return ret[0]

    def close(self):
        self.con.close()


def getData(api):
    request = req.get(url+api)
    return request.json()


if __name__ == '__main__':
    db = ProblemDB()
    db.initTable()
    print('fin set db')
    data = getData('problemset.problems')
    print('fin get data')
    for d in data['result']['problems']:
        db.addProblem(d)
    db.close()
