import Database as db
import requests as req
import json
import time

from operator import itemgetter
from pyquery import PyQuery as pq
from contestDB import ContestDB
from fileDB import FileDB
from acceptanceDB import AcceptanceDB

base_url = 'http://codeforces.com/'
url = base_url + 'api/'

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


def acceptanceRatio_old():
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


def acceptanceRatio():
    contest = getContestTable()

    pdb = ProblemDB()
    adb = AcceptanceDB()
    problems = pdb.getProblems()
    prob_data = adb.getProblems()

    result = []
    for ac, prob in zip(prob_data, problems):
        cont = contest[prob['contestId']]
        if ac['submission'] is None:
            continue
        if ac['submission'] == 0:
            ac_rate = -1
        else:
            ac_rate = ac['solved']/ac['submission']
        row = [
            '"%s"' % cont['name'],
            ac['id'],
            ac['solved'],
            ac['submission'],
            ac_rate,
        ]
        # row = list(map(str, row))
        result.append(row)
        # update TODO
        # pdb.update({'acceptance_rate': ac_rate}, prob['id'])
    writeData('data/ac_rate_new2.csv', result)
    pdb.close()
    adb.close()
    return result


def divide(list_data, n):
    par_min = 0
    par_max = 1
    step = (par_max-par_min)/n
    cur = []
    res = [cur]
    idx = 0
    max_par = 0
    for data in list_data:
        max_par = max(max_par, data[4])
        if par_min + step*(idx+1) <= data[4]:
            cur = []
            res.append(cur)
            idx += 1
        cur.append(data)
    return res


title = [
    'contest name',
    'problem id',
    'solved',
    'submissions',
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
    divisions = 5
    problem_data = acceptanceRatio()
    valid_data = filter(lambda x: x[3] > 30, problem_data)
    sorted_data = sorted(valid_data, key=itemgetter(4))
    divided_data = divide(sorted_data, divisions)

    for i, level_data in enumerate(divided_data):
        updateLevel(level_data, divisions-i)
        writeData('data/levels/level_%d.csv' % (divisions-i), level_data)


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


def getAllSubmissionNumber(contest_id, index, filter='anyVerdict'):
    time.sleep(0.8)
    url = base_url + '/problemset/status/%d/problem/%s' % (contest_id, index)
    payloads = {
        'action':'setupSubmissionFilter',
        'frameProblemIndex': index,
        'verdictName': filter,
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

    pages = dom('span.page-index')
    if len(pages) > 0:
        last_page = pq(pages[-1]).text()
    # print('%d, %d, %s' % (rejected, accepted, next_page))
        time.sleep(0.8)
        dom = pq(session.get(url + '/page/' + last_page).text)
    else:
        last_page = 1
    submission = len(dom('span.submissionVerdictWrapper')) + (int(last_page)-1)*50
    return submission


def setSubmissionNumbers():
    pdb = ProblemDB()
    problems = pdb.getProblems()
    for i, prob in enumerate(problems):
        print('%d/%d' % (i+1, len(problems)))
        contest_id = prob['contestId']
        index = prob['prob_index']
        if not prob['submission'] is None:
            continue
        try:
            submits = getAllSubmissionNumber(contest_id, index)
        except:
            print('error: ' + prob['id'])
            time.sleep(1)
            continue
        pdb.update({'submission': submits}, prob['id'])
        pdb.commit()
    pdb.close()


if __name__ == '__main__':
    culcLevels()
