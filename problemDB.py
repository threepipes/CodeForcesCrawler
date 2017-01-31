import Database as db
import requests as req
import json
import time

from operator import itemgetter
from pyquery import PyQuery as pq
from contestDB import ContestDB

base_url = 'http://codeforces.com/'
url = base_url + 'api/'

class ProblemDB:
    table_name = 'ProblemTable'
    key = 'id'
    cols = [
        'id',
        'contestId',
        'prob_index',
        'points',
        'solved',
        'level'
    ]

    def __init__(self):
        self.con = db.Connector()

    def initTable(self, drop_table=False):
        prob_table = {
            'id': 'VARCHAR(20)',
            'contestId': 'INT(10)',
            'prob_index': 'VARCHAR(5)',
            'points': 'INT(5)',
            'solved': 'INT(5)',
            'level': 'INT(2)'
        }
        self.con.createTable(self.table_name, prob_table, primary_key=self.key, drop=drop_table)

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

    def update(self, prob, keyname):
        self.con.update(prob, self.table_name, {self.key: keyname})

    def getProblem(self, where):
        ret = self.con.get(self.table_name, self.cols, where)
        if len(ret) == 0:
            return None
        return ret[0]

    def getProblems(self, where=None):
        ret = self.con.get(self.table_name, self.cols, where)
        return ret

    def close(self):
        self.con.close()


def getData(api):
    request = req.get(url+api)
    return request.json()


def setSolvedToDB():
    prob_solved = []
    prob_id = []
    for i in range(33):
        print('%d/%d' % (i+1, 33))
        dom = pq(base_url + 'problemset/page/%d' % (i+1))
        dom = pq(dom('div.datatable'))
        for elm in pq(dom('td[style="font-size:1.1rem;"]')):
            d = pq(elm)
            solved = d.text()[1:]
            prob_solved.append(solved)
            # print('%s\t%s' % (d.text(), ))
        for elm in pq(dom('td.id')):
            prob_id.append(pq(elm).text())
        time.sleep(1)
    # print(list(zip(prob_id, prob_solved)))
    db = ProblemDB()
    for pid, solved in zip(prob_id, prob_solved):
        db.update({'solved': solved}, pid)
    db.close()


def acceptanceRatio():
    cdb = ContestDB()
    contest_list = cdb.getContests()
    cdb.close()
    contest = {}
    for cont in contest_list:
        contest[cont['contestId']] = cont

    pdb = ProblemDB()
    problems = pdb.getProblems()

    result = []
    for prob in problems:
        cont = contest[prob['contestId']]
        if cont['contestant'] is None:
            continue
        if cont['contestant'] == 0:
            ac_rate = -1
        else:
            ac_rate = prob['solved']/cont['contestant']
        row = [
            '"%s"' % cont['name'],
            prob['id'],
            prob['solved'],
            cont['contestant'],
            prob['points'],
            ac_rate,
        ]
        # row = list(map(str, row))
        result.append(row)
    writeData('data/ac_rate_new.csv', result)
    pdb.close()
    return result


def divide(list_data, n):
    size = len(list_data)
    each = size//n
    return [list_data[i*each : min((i+1)*each, size)] for i in range(n)]


title = [
    'contest name',
    'problem id',
    'solved',
    'contestant',
    'points',
    'acceptance rate',
]
def writeData(filepath, result):
    with open(filepath, 'w') as f:
        f.write(','.join(title) + '\n')
        for row in result:
            row = list(map(str, row))
            f.write(','.join(row) + '\n')


def initDB():
    db = ProblemDB()
    db.initTable()
    print('fin set db')
    data = getData('problemset.problems')
    print('fin get data')
    for d in data['result']['problems']:
        db.addProblem(d)
    db.close()


def culcLevels():
    problem_data = acceptanceRatio()
    valid_data = filter(lambda x: x[3] > 30, problem_data)
    sorted_data = sorted(valid_data, key=itemgetter(5))
    divided_data = divide(sorted_data, 10)

    for i, level_data in enumerate(divided_data):
        updateLevel(level_data, 10-i)
        writeData('data/levels/level_%d.csv' % (i+1), level_data)


def updateLevel(data, level):
    db = ProblemDB()
    for row in data:
        prob_id = row[1]
        db.update({'level': level}, prob_id)


if __name__ == '__main__':
    culcLevels()
