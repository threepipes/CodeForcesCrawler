import sys
from datetime import datetime, timedelta

import requests as req
from pyquery import PyQuery as pq

from database.acceptanceDB import AcceptanceDB
from database.contestDB import ContestDB, mining_contest
from database.fileDB import FileDB
from database.problemDB import ProblemDB
from database.userDB import UserDB, UserSubmissionDB
from util.SleepTimer import SleepTimer

base_url = 'http://codeforces.com/'

"""
order for update
competition table
participant table -> file table, problem table
participant_sub table
acceptance table
"""

AcceptanceDB.foreign_key = {
    'problem_id': ProblemDB.table_name
}
ProblemDB.foreign_key = {
    'competition_id': ContestDB.table_name
}
FileDB.foreign_key = {
    'user_name': UserDB.table_name,
    'competition_id': ContestDB.table_name
}
UserSubmissionDB.foreign_key = {
    'user_name': UserDB.table_name
}

contest_db = ContestDB()
user_db = UserDB()
user_sub_db = UserSubmissionDB()
file_db = FileDB()
prob_db = ProblemDB()
acc_db = AcceptanceDB()

dblist = [
    contest_db,
    user_db,
    user_sub_db,
    file_db,
    prob_db,
    acc_db
]

timer = SleepTimer()

def drop_tables():
    for db in reversed(dblist):
        db.drop()


def init_all():
    for db in dblist:
        print('initializing '+db.table_name)
        db.init_table(drop=True)


def access_api(api, option={}):
    url = base_url + 'api/'
    timer.sleep(0.4)
    request = req.get(url+api, params=option)
    timer.reset()
    return request.json()


def divide(data_list, size):
    current = []
    result = [current]
    for data in data_list:
        current.append(data)
        if len(current) == size:
            current = []
            result.append(current)
    return result


def mining_user():
    userdata_format = {
        'handle': 'user_name',
        'rating': 'rating',
        'maxRating': 'max_rating'
    }
    six_mon_ago = datetime.now() - timedelta(days=180)
    contest_list = contest_db.select(where=("start_time>'%s'" % str(six_mon_ago).split('.')[0]))
    users = set()
    for i, contest in enumerate(contest_list):
        print('getting users... %d/%d' % (i+1, len(contest_list)))
        response = access_api(
            'contest.standings',
            {'contestId': contest['competition_id'], 'showUnofficial': 'true'}
        )
        if response['status'] != 'OK':
            continue
        members = response['result']['rows']
        for party in members:
            for user in party['party']['members']:
                users.add(user['handle'])
    user_lists = divide(list(users), 1000)
    for users in user_lists:
        option = {'handles': ';'.join(users)}
        user_info = access_api('user.info', option=option)
        if user_info['status'] != 'OK':
            print('failed getting user data')
            return False
        info = user_info['result']
        for user in info:
            data = {}
            for key, attr in userdata_format.items():
                if not key in user:
                    break
                data[attr] = user[key]
            else:
                user_db.insert(data)
        user_db.commit()
    return True


def mining_problem():
    response = access_api('problemset.problems')
    if response['status'] != 'OK':
        print('failed getting problems')
        return False
    problem_list = response['result']['problems']
    for prob in problem_list:
        comp_id = prob['contestId']
        index = prob['index']
        if 'points' in prob:
            points = prob['points']
        else:
            points = 0
        data = {
            'problem_id': str(comp_id) + index,
            'prob_index': index,
            'competition_id': comp_id,
            'points': points
        }
        prob_db.insert(data)
    prob_db.commit()
    return True


def get_source_data(status, username):
    submission_id = status['id']
    contest_id = status['contestId']
    data = {}
    data['user_name'] = username
    data['submission_id'] = submission_id
    data['competition_id'] = contest_id
    data['lang'] = status['programmingLanguage']
    data['timestamp'] = str(datetime.fromtimestamp(status['creationTimeSeconds']))
    problem = status['problem']
    data['problem_id'] = str(contest_id) + problem['index']
    data['url'] = base_url + 'contest/%d/submission/%d' % (contest_id, submission_id)
    data['file_name'] = '%s_%s_%s.src' % (username, data['submission_id'], data['competition_id'])
    if contest_id > 1000:
        data['url'] = '-'
    if 'verdict' in status:
        data['verdict'] = status['verdict'][:20]
    else:
        data['verdict'] = '-'
    return data


inf = 1000000000
time_inf = inf*2
def get_recent_sources(username, n=inf, time_from=0, time_end=time_inf):
    query = {
        'handle': username,
        'count': n
    }
    response = access_api('user.status', query)
    if response['status'] == 'FAILED':
        try:
            timer.sleep(0.4)
            name = pq(base_url+'profile/'+username)('title').text()[:-len(' - Codeforces')]
            timer.reset()
            query['handle'] = name
            username = name
            response = access_api('user.status', query)
        except:
            print(username+' failed')
            return []
    submissions = response['result']
    source = []
    for status in submissions:
        if status['creationTimeSeconds'] < time_from:
            break
        if status['creationTimeSeconds'] > time_end or status['contestId'] > 100000:
            continue
        source.append(get_source_data(status, username))
    return source


our_beginning_of_mining = 1479181649
def mining_submission():
    user_list = list(user_db.select())
    now = our_beginning_of_mining # int(datetime.now().timestamp())
    time_from = now - 180 * 24 * 60 * 60
    for i, user in enumerate(user_list):
        name = user['user_name']
        print("getting %s's source (%d/%d)" % (name, i+1, len(user_list)))
        source_data = get_recent_sources(name, time_from=time_from, time_end=now)
        user_sub_db.insert({
            'user_name': name,
            'files': len(source_data)
        })
        user_sub_db.commit()
        for data in source_data:
            file_db.insert(data)
        file_db.commit()
    return True


def get_all_submission_number(contest_id, index, verdict='anyVerdict'):
    while True:
        try:
            timer.sleep(0.8)
            url = base_url + '/problemset/status/%d/problem/%s' % (contest_id, index)
            payloads = {
                'action':'setupSubmissionFilter',
                'frameProblemIndex': index,
                'verdictName': verdict,
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

            timer.sleep(0.8)
            page_data = session.post(url, data=payloads, headers=header)
            dom = pq(page_data.text)

            pages = dom('span.page-index')
            if len(pages) > 0:
                last_page = pq(pages[-1]).text()
                timer.sleep(0.8)
                dom = pq(session.get(url + '/page/' + last_page).text)
            else:
                last_page = 1
            submission = len(dom('span.submissionVerdictWrapper')) + (int(last_page)-1)*50
        except:
            print('Error. Retry.')
        else:
            break
        timer.sleep(2)
    return submission


def mining_acceptance_rate():
    problems = prob_db.select()
    for i, prob in enumerate(problems):
        print('%d/%d' % (i+1, len(problems)))
        contest_id = prob['competition_id']
        prob_id = prob['problem_id']
        index = prob['prob_index']
        submit_list_in_sample = file_db.select({'problem_id': prob_id})
        solved_in_sample = list(filter(lambda x: x['verdict'] == 'OK', submit_list_in_sample))
        submits = get_all_submission_number(contest_id, index)
        solved = get_all_submission_number(contest_id, index, verdict='OK')
        data = {
            'problem_id': prob_id,
            'submission': submits,
            'solved': solved,
            'submission_in_sample': len(submit_list_in_sample),
            'solved_in_sample': len(solved_in_sample),
            'acceptance_rate': solved/submits,
            'lastmodified': str(datetime.now()).split('.')[0],
        }
        acc_db.insert(data)
        acc_db.commit()


def construct():
    init_all()
    mining_contest(contest_db)
    mining_user()
    mining_problem()
    mining_submission()
    mining_acceptance_rate()


if __name__ == '__main__':
    args = sys.argv
    if len(args) == 1:
        print('start construct database')
        construct()
    else:
        if args[1] == '-d':
            drop_tables()
        elif args[1] == '-competition':
            mining_contest(contest_db)
        elif args[1] == '-participant':
            mining_user()
        elif args[1] == '-problem':
            mining_problem()
        elif args[1] == '-file':
            mining_submission()
        elif args[1] == '-acceptance':
            mining_acceptance_rate()
