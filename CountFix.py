from Database import Connector as Con

key_ac = 'OK'
wa = {}


def count(dic, name, cnt):
    if not name in dic:
        dic[name] = cnt
    else:
        dic[name] += cnt


def countFix(user_data, points=-1):
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
            count(wa, cnt, 1)
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

    for file_data in data:
        idx += 1
        if (idx+1) % 100000 == 0:
            print(idx)
        if file_data['user_name'] == preName:
            user.append(file_data)
        else:
            (cnt, prob) = countFix(user, points=points)
            user = []
            rating = con.get('usertable', ['rating'], {'user_name': preName})
            rate = rating[0]['rating']
            counts[preName] = cnt
            probs[preName] = prob
            user_rating[preName] = rate
        preName = file_data['user_name']

    with open('data/wa_%d.csv' % points, 'w') as f:
        for key, value in wa.items():
            f.write('%d,%d\n' % (key, value))
    with open('data/fix_%d.csv' % points, 'w') as f:
        for key in counts.keys():
            f.write('%d,%f\n' % (user_rating[key], counts[key]/probs[key]))

    print('finish writing for points: '+str(points))


def getPoints(data):
    points = set()
    for d in data:
        if d['points'] is None:
            continue
        points.add(d['points'])
    return list(points)

if __name__ == '__main__':
    con = Con()
    print('now loading...')
    data = con.get('filetable', ['file_name', 'user_name', 'verdict', 'points'])
    print('finish getting data')

    points = getPoints(data)
    print(points)
    for p in sorted(points):
        if (p < 100) or (p in [3500, 5000]):
            continue
        getStatistics(data, p)
