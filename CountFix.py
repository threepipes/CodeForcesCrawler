from Database import Connector as Con

key_ac = 'OK'
wa = {}


def count(dic, name, cnt):
    if not name in dic:
        dic[name] = cnt
    else:
        dic[name] += cnt


def countFix(user_data):
    pre_pid = -1
    count_all = 0
    cnt = 0
    probs = 0
    for data in user_data:
        file_name = data['file_name'][:-4]
        pid = int(file_name.split('_')[-1])
        verdict = data['verdict']
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
    return count_all/probs

if __name__ == '__main__':
    con = Con()
    print('now loading...')
    data = con.get('filetable', ['file_name', 'user_name', 'verdict'])
    print('finish getting data')
    preName = data[0]['user_name']
    user = []
    user_avg = {}
    idx = 0

    for file_data in data:
        idx += 1
        if (idx+1) % 10000 == 0:
            print(idx)
        if file_data['user_name'] == preName:
            user.append(file_data)
        else:
            avg = countFix(user)
            user = []
            rating = con.get('usertable', ['rating'], {'user_name': preName})
            user_avg[rating[0]['rating']] = avg
        preName = file_data['user_name']

    with open('wa.csv', 'w') as f:
        for key, value in wa.items():
            f.write('%d,%d\n' % (key, value))
    with open('fix.csv', 'w') as f:
        for key, value in user_avg.items():
            f.write('%d,%f\n' % (key, value))
