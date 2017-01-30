from Database import Connector as Con
from problemDB import ProblemDB

key_ac = 'OK'
wa = {}


def count(dic, name, idx, cnt):
    if not name in dic:
        dic[name] = [0]*8
    dic[name][idx] += cnt


def countFix(user_data, rating, points=-1):
    pre_pid = -1
    count_all = 0
    cnt = 0
    probs = 0
    for data in user_data:
        file_name = data['file_name'][:-4]
        pid = int(file_name.split('_')[-1])
        verdict = data['verdict']
        if points >= 0 and (not 'points' in data or data['points'] != points):
            continue
        if pid == -pre_pid:
            continue
        if pid != pre_pid:
            probs += 1
            cnt = 0
        if verdict == 'OK':
            count(wa, cnt, rating//500, 1)
            count_all += cnt
            cnt = 0
        else:
            cnt += 1
        pre_pid = pid
    if probs == 0:
        probs = -1
    return (count_all, probs)


def add(dic, key, value):
    if not key in dic:
        dic[key] = 0
    dic[key] += value


def getStatistics(data, points):
    preName = data[0]['user_name']
    user = []
    user_rating = {}
    counts = {}
    probs = {}
    idx = 0
    user_count = set()
    wa.clear()

    for file_data in data:
        idx += 1
        if (idx+1) % 100000 == 0:
            print(idx)
        if file_data['user_name'] == preName:
            user.append(file_data)
        else:
            rating = con.get('usertable', ['rating'], {'user_name': preName})
            rate = rating[0]['rating']
            (cnt, prob) = countFix(user, rate, points=points)
            user = []
            counts[preName] = cnt
            probs[preName] = prob
            user_rating[preName] = rate
            if cnt > 0:
                user_count.add(preName)
        preName = file_data['user_name']

    divisions = [0]*8
    for name in user_count:
        divisions[user_rating[name]//500] += 1
    divisions = map(str, divisions)

    with open('data/fix/wa_%d.csv' % points, 'w') as f:
        f.write('freq,count/submitted_user,count_all,0..499,500..999,1000..1499,1500..1999,2000..2499,2500..2999,3000..3499,3500..3999,submitted_user\n')
        size = len(user_count)
        for key, value in wa.items():
            v_sum = sum(value)
            f.write('%d,%f,%d,%s,%d\n' % (key, v_sum/size, v_sum, ','.join(map(str, value)), size))
    # with open('data/fix/fix_%d.csv' % points, 'w') as f:
    #     for key in counts.keys():
    #         f.write('%d,%f,%d\n' % (user_rating[key], counts[key]/probs[key], counts[key]))
    with open('data/fix/user_numbers_rating.csv', 'a') as f:
        # f.write('rating,%s\n' % ','.join(title))
        f.write('%d,%s\n' % (points, ','.join(divisions)))
    print('finish writing for points: '+str(points))


def getPoints(data):
    points = set()
    for d in data:
        if d['points'] is None:
            continue
        points.add(d['points'])
    return list(points)


def getProblemTable():
    pdb = ProblemDB()
    probs = pdb.getProblems(where=None)
    table = {}
    for prob in probs:
        pid = prob['prob_index']
        cid = prob['contestId']
        points = prob['points']
        if not cid in table:
            table[cid] = {'-': 0}
        table[cid][pid] = points
    pdb.close()
    return table


def writeData(data_list):
    with open('log.txt', 'w') as f:
        for data in data_list:
            f.write(str(data)+'\n')

if __name__ == '__main__':
    table = getProblemTable()
    con = Con()
    print('now loading...')
    cols = [
        'file_name',
        'user_name',
        'verdict',
        'contestId',
        'prob_index'
    ]
    data = con.get('filetable', cols, where='contestId<10000')
    count_none = 0
    has_null = set()
    for d in data:
        try:
            d['points'] = table[d['contestId']][d['prob_index']]
        except:
            has_null.add(d['user_name'])
            d['points'] = 0

    print('finish getting data')
    writeData(has_null)
    points = getPoints(data)
    print(points)

    title = map(str, list(range(0, 4000, 500)))
    with open('data/fix/user_numbers_rating.csv', 'w') as f:
        f.write('rating,%s\n' % ','.join(title))
    for p in sorted(points):
        if (p < 100) or (p in [3500, 5000]):
            continue
        getStatistics(data, p)
