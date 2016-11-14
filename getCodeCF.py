from pyquery import PyQuery as pq
import requests as req
import time
import json
import os, os.path
from Database import Database

base_url = 'http://codeforces.com/'
url = base_url + 'api/'
userfile = 'data/users.json'

inf = 10000000


def getData(api, option):
    time.sleep(1)
    return req.get(url+api, params=option).json()


# get user list from codeforces (consume some time)
def getUserData(option):
    if not os.path.isfile(userfile):
        users = getData('user.ratedList', {'activeOnly': 'true'})
        saveAsJson(users, userfile)
        return users
    else:
        return loadData(userfile)


# get n users with some information (currently: handle, rating, max_rating)
def getUsers(datalist, n=inf):
    users = getUserData({'activeOnly': 'true'})['result']
    user_list = []
    count = 0
    for user in users:
        count += 1
        if count > n:
            break
        data = {}
        for (cf_name, db_name) in datalist.items():
            if not cf_name in user:
                print('Wrong datalist. Key %s was not found' % cf_name)
            data[db_name] = user[cf_name]
        user_list.append(data)
    return user_list


# save json data as txt
def saveAsJson(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data))


def getSource(prob_id, contest_id):
    time.sleep(1)
    dom = pq(base_url + 'contest/%d/submission/%d' % (contest_id, prob_id))
    return dom.find('pre.prettyprint.program-source').text()


def getSourceData(status, src=True):
    prob_id = status['id']
    contest_id = status['contestId']
    data = {}
    if src:
        data['source'] = getSource(prob_id, contest_id)
    data['prob_id'] = prob_id
    data['contest_id'] = contest_id
    data['lang'] = status['programmingLanguage']
    if 'verdict' in status:
        data['verdict'] = status['verdict'][:20]
    else:
        data['verdict'] = '-'
    return data


# get recent n sources
# return source list (which creationTimeSeconds is larger than "time")
def recentSources(username, n=inf, time_border=0, src=True):
    query = {
        'handle': username,
        'count': n
    }
    submissions = getData('user.status', query)['result']
    source = []
    print("%s's source" % username)
    for status in submissions:
        if status['creationTimeSeconds'] < time_border:
            break
        # print('getting source id=%d' % status['id'])
        source.append(getSourceData(status, src))
    return source


def loadData(filename):
    data = None
    with open(filename, encoding='utf-8') as f:
        data = json.loads(f.read())
    return data


def saveFile(filename, content):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)


def init():
    if not os.path.isdir('data'):
        os.mkdir('data')


month_before = 6
def getLeastTime():
    sec = time.time() - month_before*30*24*60*60
    return int(sec)


filename = 'data/sample.json'
userdata_format = {
    'handle': 'user_name',
    'rating': 'rating',
    'maxRating': 'max_rating'
}
if __name__ == '__main__':
    init()

    # get 10 users
    user_list = getUsers(userdata_format)
    db = Database()
    db.initTables()

    border = getLeastTime()

    # from username, getting recent 2 source files and register to DB
    for user in user_list[-500:]:
        db.addUser(user)
        handle = user['user_name']
        source = recentSources(handle, time_border=border, src=False)
        for src in source:
            filename = '%s_%s_%s.src' % (handle, src['prob_id'], src['contest_id'])
            if 'source' in src:
                saveFile('data/'+filename, src['source'])
            db.addFile(handle, filename, src['lang'], src['verdict'])

    # show DB tables
    # print('UserTable: ')
    # db.showUserTable()
    # print('FileTable: ')
    # db.showFileTable()

    db.close()
