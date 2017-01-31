import Database as db
import requests as req
import json
import time

from operator import itemgetter
from pyquery import PyQuery as pq
from contestDB import ContestDB
from fileDB import FileDB

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
        'level',
        'try_in_sample',
        'solved_in_sample',
        'submission',
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

    def commit(self):
        self.con.commit()


def getData(api, option=None):
    request = req.get(url+api, params=option)
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


def getContestTable():
    cdb = ContestDB()
    contest_list = cdb.getContests()
    cdb.close()
    contest = {}
    for cont in contest_list:
        contest[cont['contestId']] = cont
    return contest


def acceptanceRatio():
    contest = getContestTable()

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
            ac_rate = prob['solved']**1.3/cont['contestant']
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


def acceptanceRatio_new():
    contest = getContestTable()

    pdb = ProblemDB()
    problems = pdb.getProblems()

    result = []
    for prob in problems:
        cont = contest[prob['contestId']]
        if prob['submission'] is None:
            continue
        if prob['submission'] == 0:
            ac_rate = -1
        else:
            ac_rate = prob['solved']**1.3/prob['submission']
        row = [
            '"%s"' % cont['name'],
            prob['id'],
            prob['solved'],
            prob['submission'],
            prob['points'],
            ac_rate,
        ]
        # row = list(map(str, row))
        result.append(row)
    writeData('data/ac_rate_new2.csv', result)
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
    divided_data = divide(sorted_data, 6)

    for i, level_data in enumerate(divided_data):
        # updateLevel(level_data, 10-i)
        writeData('data/levels_new/level_%d.csv' % (i+1), level_data)


def updateLevel(data, level):
    db = ProblemDB()
    for row in data:
        prob_id = row[1]
        db.update({'level': level}, prob_id)
    db.close()


def setTryAndSolve():
    fdb = FileDB()
    pdb = ProblemDB()
    problems = pdb.getProblems()
    for i, prob in enumerate(problems):
        if (i+1)%10 == 0:
            print('%d/%d' % (i+1, len(problems)))
        contest_id = prob['contestId']
        index = prob['prob_index']
        submits = fdb.getFiles({'contestId': contest_id, 'prob_index': index})
        tries = len(submits)
        ok = 0
        for submit in submits:
            if submit['verdict'] == 'OK':
                ok += 1
        pdb.update({'try_in_sample': tries, 'solved_in_sample': ok}, prob['id'])
        pdb.commit()
    pdb.close()


def getAllSubmissionNumber(contest_id, index):
    time.sleep(0.8)
    url = base_url + '/problemset/status/%d/problem/%s' % (contest_id, index)
    payloads = {
        'action':'setupSubmissionFilter',
        'frameProblemIndex': index,
        'verdictName': 'anyVerdict',
        'programTypeForInvoker': 'anyProgramTypeForInvoker',
        'comparisonType': 'NOT_USED',
        'judgedTestCount':'',
    }
    header = {
        'User-Agent': 'Mozilla/5.0'
    }
    session = req.Session()
    dom = pq(session.get(url).text)
    payloads['csrf_token'] = pq(dom('input[name="csrf_token"]')).attr('value')

    time.sleep(0.8)
    page_data = session.post(url, data=payloads, headers=header)
    dom = pq(page_data.text)

    last_page = pq(dom('span.page-index')[-1]).text()
    # print('%d, %d, %s' % (rejected, accepted, next_page))
    time.sleep(0.8)
    dom = pq(session.get(url + '/page/' + last_page).text)
    submission = len(dom('span.submissionVerdictWrapper')) + (int(last_page)-1)*50
    return submission


def setSubmissionNumbers():
    pdb = ProblemDB()
    problems = pdb.getProblems()
    for i, prob in enumerate(problems):
        print('%d/%d' % (i+1, len(problems)))
        contest_id = prob['contestId']
        index = prob['prob_index']
        try:
            submits = getAllSubmissionNumber(contest_id, index)
        except:
            print('error')
            continue
        pdb.update({'submission': submits}, prob['id'])
        pdb.commit()
    pdb.close()


if __name__ == '__main__':
    setSubmissionNumbers()
