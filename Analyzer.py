from fileDB import FileDB
from userDB import UserDB
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
    cmd = ['java', '-jar', jar_path, '-j', '-s', 'filelist.txt']
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


def writeData(result):
    udb = UserDB()
    users = udb.getAllUserWithRating()
    utor = {}
    for user in users:
        utor[user['user_name']] = user['rating']
    keywords = []
    with open('data/keyword') as f:
        for line in f:
            keywords.append(line.strip())
    with open('data/analysis_result.csv', 'w') as f:
        f.write('user,rating,'+','.join(keywords)+'\n')
        for data in result:
            f.write('"%s",%d' % (data['user_name'], utor[data['user_name']]))
            for key in keywords:
                d = 0
                if key in data['data']:
                    d = data['data'][key]
                f.write(',%d' % d)
            f.write('\n')


if __name__ == '__main__':
    files = getFileFromProbId(712, 'B')
    print('finish getting file list')
    writeToFileList(files)
    result = analyze('analyze.jar', files)
    writeData(result)
