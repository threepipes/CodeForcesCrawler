from fileDB import FileDB
from userDB import UserDB
from problemDB import ProblemDB
from subprocess import *
import random
import json


def getUsers():
    udb = UserDB()
    users = udb.getAllUser()
    udb.close()
    return users


def getFilenames(fdb, username, limit, where=None):
    file_filter = {'user_name': username}
    if not where is None:
        file_filter.update(where)
    return fdb.getFiles(file_filter, limit)


def chooseSampleFiles(user_num=1000, file_num_each=1):
    users = getUsers()
    sample_list = random.sample(users, user_num)
    fdb = FileDB()
    files = []
    failed = 0
    file_filter = {'lang': 'GNU C++11', 'verdict': 'OK'}
    for i, user in enumerate(sample_list):
        if (i+1)%1000 == 0:
            print(i+1)
        file_list = getFilenames(fdb, user, file_num_each, file_filter)
        if len(file_list) == 0:
            failed += 1
            continue
        files += file_list
    print('failed num: '+str(failed))
    return files


def getFileFromProbId(contest_id, prob_index, limit=-1):
    file_filter = {
        'lang': 'GNU C++11',
        'verdict': 'OK',
        'contestId': contest_id,
        'prob_index': prob_index
    }
    fdb = FileDB()
    return fdb.getFiles(file_filter, limit)


def writeToFileList(files):
    with open('data/filelist.txt', 'w', encoding='utf-8') as f:
        for data in files:
            f.write('%s %s\n' % ('src/' + data['file_name'], data['lang'].replace(' ', '_')))


def analyze(jar_path, files):
    cmd = ['java', '-jar', jar_path, '-e', '-j', '-s', 'filelist.txt']
    pipe = Popen(cmd, cwd='data', stdout=PIPE, stderr=None).stdout
    idx = 0
    # print(files)
    result = []
    ok = 0
    for line in pipe.readlines():
        data = json.loads(line.decode('utf-8').strip())
        # print(data)
        while idx < len(files) and files[idx]['file_name'] != data['src_name']:
            # print('not found '+files[idx]['file_name'])
            idx += 1
        if idx < len(files):
            ok += 1
            file_data = files[idx]
            del data['src_name']
            file_data['data'] = data
            result.append(file_data)
            # print(file_data)
        else:
            break
    print('finish analyze. %d/%d files were analyzed.' % (ok, len(files)))
    return result


def getMode(multiset):
    max_value = 0
    max_idx = 0
    for k, v in multiset.items():
        if v > max_value:
            max_value = v
            max_idx = k
    return max_idx


def normalization_mode(result, keywords):
    mode = {}
    for kw in keywords:
        multiset = {}
        for data in result:
            d = data['data']
            if not kw in d:
                d[kw] = 0
                continue
            num = d[kw]
            if not num in multiset:
                multiset[num] = 0
            multiset[num] += 1
        mode[kw] = getMode(multiset)
    print(mode)
    for kw in keywords:
        if mode[kw] == 0:
            continue
        for data in result:
            data['data'][kw] /= mode[kw]


def normalization_median(result, keywords):
    median = {}
    for kw in keywords:
        count = []
        for data in result:
            d = data['data']
            if not kw in d:
                d[kw] = 0
                continue
            count.append(d[kw])
        if len(count) == 0:
            median[kw] = 0
            continue
        median[kw] = sorted(count)[len(count)//2]
    # print(median)
    for kw in keywords:
        if median[kw] == 0:
            continue
        for data in result:
            data['data'][kw] /= median[kw]


def getDictUserToRating():
    udb = UserDB()
    users = udb.getAllUserWithRating()
    utor = {}
    for user in users:
        utor[user['user_name']] = user['rating']
    return utor


def writeData(result, keywords):
    utor = getDictUserToRating()
    normalization_median(result, keywords)
    with open('data/analysis_result_norm.csv', 'w') as f:
        f.write('user,rating,'+','.join(keywords)+'\n')
        for data in result:
            f.write('"%s",%d' % (data['user_name'], utor[data['user_name']]))
            for key in keywords:
                d = 0
                if key in data['data']:
                    d = data['data'][key]
                f.write(',%f' % d)
            f.write('\n')


def getKeywords():
    keywords = []
    with open('data/keyword') as f:
        for line in f:
            keywords.append(line.strip())
    return keywords


def setData(result, data, keywords):
    for res in result:
        name = res['user_name']
        if not name in data:
            data[name] = {}
            for key in keywords:
                data[name][key] = 0
            data[name]['prob_num'] = 0
        d = res['data']
        for key in keywords:
            data[name][key] += d[key]
        data[name]['prob_num'] += 1


def statistics(border=0):
    pdb = ProblemDB()
    problems = pdb.getProblems('points>100')
    keywords = getKeywords()
    data = {}
    for prob in problems:
        print(prob['id'])
        files = getFileFromProbId(prob['contestId'], prob['prob_index'])
        writeToFileList(files)
        result = analyze('analyze.jar', files)
        if len(result) < border:
            continue
        normalization_median(result, keywords)
        setData(result, data, keywords)

    utor = getDictUserToRating()
    with open('data/statistics_nonfiltered.csv', 'w') as f:
        for key, each in data.items():
            f.write('"%s",%d' % (key, utor[key]))
            for kw in keywords:
                f.write(',%f' % (each[kw]/each['prob_num']))
            f.write('\n')


def testAnalysis():
    files = getFileFromProbId(712, 'B')
    print('finish getting file list')
    writeToFileList(files)
    result = analyze('analyze.jar', files)
    keywords = getKeywords()
    writeData(result, keywords)


if __name__ == '__main__':
    statistics()
