from pyquery import PyQuery as pq
import requests as req
import time
import json
import os, os.path
from Database import Database
from fileDB import FileDB
import random
import SleepTimer

base_url = 'http://codeforces.com/'
url = base_url + 'api/'
userfile = 'data/users.json'
samplefile = 'data/sampleUsers.json'

inf = 1000000000
time_inf = inf*2
timer = None

def getData(api, option):
    timer.sleep(0.4)
    request = req.get(url+api, params=option)
    timer.reset()
    return request.json()


# get user list from codeforces (consume some time)
def getUserData(option):
    if not os.path.isfile(userfile):
        users = getData('user.ratedList', {'activeOnly': 'true'})
        saveAsJson(users, userfile)
        return users
    else:
        return loadData(userfile)


def getSampleUsers(datalist, n):
    if not os.path.isfile(samplefile):
        user_list = getUsers(datalist)
        sample_list = random.sample(user_list, n)
        saveAsJson(sample_list, samplefile)
        print('saved sample users')
        return sample_list
    else:
        return loadData(samplefile)


def setSubmissionHistory(db, users, time_from, time_end):
    # db.createSampleTableIfNotExists()
    # print('start getting submissions')
    for user in users:
        # db.addUser(user)
        handle = user['user_name']
        try:
            source = recentSources(handle, time_from=time_from, time_end=time_end, src=False)
        except:
            print('error '+handle)
            continue
        if len(source) == 0:
            continue
        # db.addSampleUser(handle, len(source))
        for src in source:
            filename = '%s_%s_%s.src' % (handle, src['prob_id'], src['contest_id'])
            src['file_name'] = filename
            db.addFile(src)


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
    timer.sleep(1)
    dom = pq(base_url + 'contest/%d/submission/%d' % (contest_id, prob_id))
    timer.reset()
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
    data['timestamp'] = status['creationTimeSeconds']
    problem = status['problem']
    data['prob_index'] = problem['index']
    data['url'] = base_url + 'contest/%d/submission/%d' % (contest_id, prob_id)
    if contest_id > 1000:
        data['url'] = '-'
    if 'verdict' in status:
        data['verdict'] = status['verdict'][:20]
    else:
        data['verdict'] = '-'
    return data


# get recent n sources
# return source list (which creationTimeSeconds is larger than "time")
def recentSources(username, n=inf, time_from=0, time_end=time_inf, src=True):
    query = {
        'handle': username,
        'count': n
    }
    response = getData('user.status', query)
    if response['status'] == 'FAILED':
        try:
            timer.sleep(0.4)
            name = pq(base_url+'profile/'+username)('title').text()[:-len(' - Codeforces')]
            timer.reset()
            query['handle'] = name
            username = name
            response = getData('user.status', query)
        except:
            print(username+' failed')
            return []
    submissions = response['result']
    source = []
    print("%s's source" % username)
    for status in submissions:
        if status['creationTimeSeconds'] < time_from:
            break
        if status['creationTimeSeconds'] > time_end:
            continue
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
end = 1479181649
def getLeastTime():
    sec = end - month_before*30*24*60*60
    return int(sec)


idx_file = 'data/lastIdx.dat'
def last():
    idx = 0
    with open(idx_file) as f:
        idx = int(f.read().strip())
    return idx


filename = 'data/sample.json'
userdata_format = {
    'handle': 'user_name',
    'rating': 'rating',
    'maxRating': 'max_rating'
}
def getSamples():
    db = Database()
    filenames = db.getSampleFilenames()
    idx = 0
    while True:
        length = len(filenames)
        try:
            for filename in filenames[idx:]:
                if os.path.isfile('data/src/'+filename):
                    idx += 1
                    continue
                print('%d/%d' % (idx+1, length))
                items = filename[:-4].split('_')
                source = getSource(int(items[-2]), int(items[-1]))
                saveFile('data/src/'+filename, source)
                # saveFile('//nas2/s-tutumi/codeforces/src/'+filename, source)
                idx += 1
        except:
            print('Error in idx: '+str(idx))
            saveFile(idx_file, str(idx))
        time.sleep(15)

    db.close()


def countMiss():
    db = Database()
    filenames = db.getSampleFilenames()
    count = 0
    for i, filename in enumerate(filenames):
        if (i+1)%10000 == 0:
            print('fin '+str(i+1))
        if not os.path.isfile('data/src/'+filename):
            count += 1
    db.close()
    print(count)


def setUsersToDB():
    # with open('has_null.txt') as f:
    #     user_list = [{'user_name': row.strip()} for row in f]
    user_list = getUsers(userdata_format)
    border = getLeastTime()
    # samples = set()
    # for user in sample_user:
    #     samples.add(user['user_name'])
    # newlist = []
    fdb = FileDB()
    # flag = False
    index = 'prob_index'
    for i, user in enumerate(user_list):
        # if not user['user_name'] in samples:
        # if user['user_name'] == 'SwapnilDGr8':
        #     flag = True
        # if not flag:
        #     continue
        if (i+1)%100 == 0:
            fdb.con.connector.commit()
            print('%d/%d' % (i, len(user_list)))
        # if not fdb.hasNull(user['user_name'], 'points'):
        #     continue
        # newlist.append(user)
        file_list = fdb.getFiles({'user_name': user['user_name']})
        for fd in file_list:
            if fd['timestamp'] is None:
                continue
            if not index in fd or fd[index] is None or fd[index] == '-':
                setSubmissionHistory(fdb, [user], border, end)
                break
    fdb.close()


def checkDB():
    # with open('has_null.txt') as f:
    #     user_list = [{'user_name': row.strip()} for row in f]
    user_list = getUsers(userdata_format)
    border = getLeastTime()
    # samples = set()
    # for user in sample_user:
    #     samples.add(user['user_name'])
    # newlist = []
    fdb = FileDB()
    # flag = False
    index = 'prob_index'
    blacklist = []
    for i, user in enumerate(user_list):
        # if not user['user_name'] in samples:
        # if user['user_name'] == 'SwapnilDGr8':
        #     flag = True
        # if not flag:
        #     continue
        if (i+1)%100 == 0:
            print('%d/%d' % (i, len(user_list)))
        # if not fdb.hasNull(user['user_name'], 'points'):
        #     continue
        # newlist.append(user)
        file_list = fdb.getFiles({'user_name': user['user_name']})
        for fd in file_list:
            if fd['timestamp'] is None:
                continue
            if not index in fd or fd[index] is None or fd[index] == '-':
                blacklist.append(user)
                break
        if len(blacklist)>10:
            break
    print(blacklist)
    print(len(blacklist))
    fdb.close()


if __name__ == '__main__':
    # countMiss()
    timer = SleepTimer.SleepTimer()
    # setUsersToDB()
    getSamples()
    # checkDB()
    # user_list = getUsers(userdata_format)
    # target = -1
    # for i, user in enumerate(user_list):
    #     if user['user_name'] == 'MrBear':
    #         print(i)
