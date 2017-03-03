from subprocess import *
from fileDB import FileDB
from userDB import UserDB
from acceptanceDB import AcceptanceDB
import json
import copy
import time


class LevelStat:
    def __init__(self, level):
        self.level = level
        self.each_max = 0
        self.prob_max = 0
        self.diff_sum = 0
        self.each_count = 0
        self.prob_count = 0

    def update(self, prob_stat):
        total = 0
        for diff in prob_stat:
            total += diff
            self.each_max = max(self.each_max, diff)
        self.prob_count += 1
        self.each_count += len(prob_stat)
        self.diff_sum += total
        self.prob_max = max(self.prob_max, total)

    def __str__(self):
        if self.each_count == 0:
            self.each_count = -1
        if self.prob_count == 0:
            self.prob_count = -1
        return ','.join(map(str, [
            self.each_count,
            self.diff_sum/self.each_count,
            self.each_max,
            self.prob_count,
            self.diff_sum/self.prob_count,
            self.prob_max
        ]))


class TotalStat:
    def __init__(self):
        self.stats = [LevelStat(i) for i in range(10)]
        self.level_dict = self.set_level_dict()

    def set_level_dict(self):
        adb = AcceptanceDB()
        accs = adb.select(col=['problem_id', 'acceptance_rate'])
        levels = {}
        for prob in accs:
            levels[prob['problem_id']] = int(prob['acceptance_rate']*10)
        adb.close()
        return levels

    def update(self, prob_result):
        pid = prob_result['pid']
        if not pid in self.level_dict:
            return
        level = self.level_dict[pid]
        self.stats[level].update(prob_result['statistics'])

    def __str__(self):
        diff_sum = 0
        each_fix_max = 0
        each_fix_count = 0
        prob_fix_max = 0
        prob_fix_count = 0
        for prob_stat in self.stats:
            each_fix_max = max(each_fix_max, prob_stat.each_max)
            prob_fix_max = max(prob_fix_max, prob_stat.prob_max)
            diff_sum += prob_stat.diff_sum
            each_fix_count += prob_stat.each_count
            prob_fix_count += prob_stat.prob_count
        if each_fix_count == 0:
            each_fix_count = -1
        if prob_fix_count == 0:
            prob_fix_count = -1
        return ','.join(map(str, [
            each_fix_count,
            diff_sum/each_fix_count,
            each_fix_max,
            prob_fix_count,
            diff_sum/prob_fix_count,
            prob_fix_max
        ])) + ',' + ','.join(map(str, self.stats))


def append_dict(dic, key, value):
    if not key in dic:
        dic[key] = []
    dic[key].append(value)


def statistics_distances(dists):
    return dists


tmpfile = '../data/filelist_comp.txt'
def analyze_user_files(jar_path, files):
    with open(tmpfile, 'w') as f:
        for row in files:
            f.write(' '.join(row['content'])+'\n')

    cmd = ['java', '-jar', jar_path, '-comp', tmpfile]
    pipe = Popen(cmd, cwd='../data', stdout=PIPE, stderr=None).stdout
    result = []
    for line in pipe.readlines():
        data = json.loads(line.decode('utf-8').strip())
        result.append(statistics_distances(data))
    return result


base_dir = 'C:/Work/Python/Lab/CodeForcesCrawler/data/src/'
def repack_files(file_lists: dict):
    result = []
    for pid, files in file_lists.items():
        sub_list = []
        for f in files:
            sub_list.append(base_dir + f['file_name'])
            if f['verdict'] == 'OK':
                break
        result.append({'content': sub_list, 'pid': pid})
    return result


jar_path = 'analyze.jar'
file_filter = set(['GNU C++14', 'GNU C++11', 'GNU C++'])
def analyze_user(username: str, fdb: FileDB):
    file_data = fdb.select(where={'user_name': username})
    file_lists = {}
    for data in file_data:
        if data['timestamp'] is None:
            data['timestamp'] = -1
        else:
            data['timestamp'] = int(time.mktime(data['timestamp'].timetuple()))
    for data in sorted(file_data, key=lambda x: x['timestamp']):
        if not data['lang'] in file_filter:
            continue
        append_dict(file_lists, data['problem_id'], data)

    repacked = repack_files(file_lists)
    analyzed_result = analyze_user_files(jar_path, repacked)
    result = []
    for data, stat in zip(repacked, analyzed_result):
        result.append({'pid': data['pid'], 'statistics': stat})
        # print(str(data['pid'])+' '+str(stat))
    return result


columns = [
    'username',
    'rating',
]
sub_column = [
    'total_times_of_fix'# 修正回数合計
    'each_fix_avarage', # 変更履歴1つに対する変更量の平均
    'each_fix_max',     # 変更履歴1つに対する変更量の最大
    'tried_prob',       # 挑戦した問題の合計
    'prob_fix_average'  # 問題1つに対する変更量の平均
    'prob_fix_max',     # 問題1つに対する変更量の最大
]
def result_to_row(user_data, user_result):
    statistics = TotalStat()
    for prob_result in user_result:
        statistics.update(prob_result)
    row = ','.join(map(str, [
        '"%s"' % user_data['user_name'],
        user_data['rating'],
        statistics
    ]))
    return row


def header():
    row = []
    row += columns
    row += [s+'_all' for s in sub_column]
    for level in range(10):
        row += [s+'_'+str(level) for s in sub_column]
    return ','.join(row)


def analyze_all():
    udb = UserDB()
    user_list = udb.select(col=['user_name', 'rating'])
    udb.close()
    fdb = FileDB()

    with open('result_diffs.csv', 'w') as f:
        f.write(header() + '\n')
        for i, userdata in enumerate(user_list):
            if (i+1)%10 == 0:
                print('%d/%d' % (i+1, len(user_list)))
            name = userdata['user_name']
            user_result = analyze_user(name, fdb)
            row = result_to_row(userdata, user_result)
            f.write(row + '\n')

    fdb.close()


def test_part():
    udb = UserDB()
    user_list = udb.select(col=['user_name', 'rating'])
    udb.close()
    fdb = FileDB()

    for i, userdata in enumerate(user_list[16:20]):
        name = userdata['user_name']
        print(name)
        user_result = analyze_user(name, fdb)
        row = result_to_row(userdata, user_result)
    fdb.close()

if __name__ == '__main__':
    analyze_all()
