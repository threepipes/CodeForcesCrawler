import os
import json
import copy
import time
from subprocess import *
from fileDB import FileDB
from userDB import UserDB
from acceptanceDB import AcceptanceDB
from problemDB import ProblemStatDB

import boxplot as bp
import numpy as np


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
    """
    あるユーザに関して，
    問題ごとの提出リストが与えられる
    各問題の提出リストについて，隣接提出の差分を計算し，
    差分行列 result[][] を返す
    """
    with open(tmpfile, 'w') as f:
        for row in files:
            f.write(' '.join(row['content'])+'\n')

    cmd = ['java', '-jar', jar_path, '-comp', tmpfile]
    pipe = Popen(cmd, cwd='../data', stdout=PIPE, stderr=None).stdout
    result = []
    # idx = 0 # debug
    for line in pipe.readlines():
        data = json.loads(line.decode('utf-8').strip())
        result.append(statistics_distances(data))
        # --- debug ---
        # for f, d in zip(files[idx]['content'], data):
        #     if d > 300:
        #         print(data)
        #         print(files[idx]['content'])
        #         break
        # idx += 1
    return result


base_dir = os.path.abspath('../data/src/')
def repack_files(file_lists: dict):
    """
    (問題番号:提出リスト) の形式で保持している辞書を，
    (pid:問題番号, content:提出リスト) のリストに変更する
    順序を保持する必要があるため
    """
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
    """
    与えられたユーザに関して，
    {pid:問題番号, statistics:差分配列} を計算して返す
    差分配列とは，提出を時系列で並べたとき，
    隣接する提出の編集距離を要素とする配列である
    """
    file_data = fdb.select(where={'user_name': username})

    # 提出を問題番号ごとにまとめる
    file_lists = {}
    for data in file_data:
        if data['timestamp'] is None:
            data['timestamp'] = -1
        else:
            data['timestamp'] = int(time.mktime(data['timestamp'].timetuple()))
    for data in sorted(file_data, key=lambda x: x['timestamp']):
        # フィルタリング: C++ かつ コンテスト最中
        if not data['lang'] in file_filter or data['during_competition'] == 0:
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
        print(userdata)
        user_result = analyze_user(name, fdb)
        print(user_result)
        row = result_to_row(userdata, user_result)
    fdb.close()


def stat_method(method: str, data):
    """
    dataが正規化済みの値である場合もあるので，
    intに変換するのは間違い
    """
    if method == 'disp':
        return float(np.var(data))
    elif method == 'max':
        return float(np.max(data))
    elif method == 'min':
        return float(np.min(data))
    elif method == 'mean':
        return float(np.mean(data))
    else:
        return float(np.median(data))


stat_types = ['disp', 'max', 'min', 'mean', 'med']
def make_stat_dict():
    stat = {}
    for t in stat_types:
        stat[t] = [[] for _ in range(len(rating_split))]
    return stat


def append_stat(stat: dict, stat_type: str, rating: int, x: float):
    """
    statに対してデータxを加える
    stat: make_stat_dictで作成された辞書．詳細は下のコメント参照
    stat_type: 分散 or 最大値 or ...
    rating: データxの持ち主のレーティング
    """
    for i, r in enumerate(rating_split):
        if rating > r:
            continue
        stat[stat_type][i].append(x)
        break


def add_statistics(diff_list: list, rating: int, stat_dict: dict):
    """
    あるユーザの差分配列を，stat_dictに加える
    分散 ～ 中央値
    """
    if len(diff_list) == 0:
        return
    dlist = np.array(diff_list)
    for method in stat_types:
        append_stat(stat_dict, method, rating, stat_method(method, dlist))


def plot_statistics(stat_dict: dict, prefix: str, ylim_list: dict):
    """
    編集距離の分散や中央値などの統計データであるstat_dictをplotする
    prefixは図の名前の先頭につける(正規化・非正規化の区別用)
    """
    for key, data_list in stat_dict.items():
        # {label:レーティング, data:統計データ(list)} の配列を作る
        plot_data = []
        for rating, data in zip(rating_split, data_list):
            plot_data.append({
                'label': '-%d' % rating,
                'data': data
            })
        save_path = '%s_%s.png' % (prefix, key)
        bp.boxplot(
            plot_data,
            label_vh=('edit distance', 'rating'),
            path=save_path,
            ylim=ylim_list[key]
        )

ylim_data = {
    'norm': {
        'disp': (0, 10000),
        'max': (0, 500),
        'min': (0, 10),
        'mean': (0, 50),
        'med': (0, 10),
    },
    'no_norm': {
        'disp': (0, 50000),
        'max': (0, 2000),
        'min': (0, 10),
        'mean': (0, 300),
        'med': (0, 100),
    },
    'norm_sub': {
        'disp': (0, 1000),
        'max': (0, 500),
        'min': (0, 10),
        'mean': (0, 100),
        'med': (0, 100),
    }
}

"""
[方針]
問題ごと中央値で割って正規化(あり版なし版両方つくる)
分散，最大値，最小値，平均，中央値 でファイルを分ける
レーティングで10段階に分割
単要素はユーザ

norm
no_norm

特徴>レーティング分割>データ
例：
{
    disp: [
        [data_0-200],
        [data_200-400],
        ...
        [data_2000-2200],
        ...
    ],
    max: [
        ...
    ],
    ...
}
特徴: disp, max, min, mean, med
[normalized]
disp: 不明 -> 10000以上除外
max: 最大3000超え，だいたい200? -> 500以上除外
min: 小さすぎて不明 -> 10以上除外
mean: だいたい10くらい, 最大300ちょい -> 50以上除外
med: 小さすぎて不明 -> 10以上除外
[raw]
disp: 不明 -> とりあえず50000以上除外
max: 最大14000超え -> 2000以上除外
min: 小さすぎて不明 -> 10以上除外
mean: だいたい100くらい, 最大1400 -> 300以上除外
med: 小さすぎて不明 -> 100以上除外
レーティング分割: rating_split


正規化するために，集計を問題ごとにする or 全要素保持しておく
下では，全要素保持を行う
中央値は何使う？
- 全要素の中央値 -> 異様にsubmitする人がいるとかたよる
- 個人ごと平均をとり，その中での中央値 -> 複雑にしすぎでは？
下では全要素の中央値: 十分submitが行われていれば，偏りはない
"""
rating_split = [
    1100, 1200, 1300, 1400, 1500, 1600, 1700, 1900, 2200, 9999
]
def boxplot_dist():
    udb = UserDB()
    user_list = udb.select(col=['user_name', 'rating'])
    udb.close()
    fdb = FileDB()

    prob_stat = {}
    for i, userdata in enumerate(user_list):
        """
        まず正規化のための中央値を計算する
        user_resultはuserdataに退避
        """
        name = userdata['user_name']
        user_result = analyze_user(name, fdb)
        userdata['result'] = user_result
        print(name, i)

        for sub_data in user_result:
            pid = sub_data['pid']
            # for dist in sub_data['statistics']:
            if not pid in prob_stat:
                prob_stat[pid] = []
            prob_stat[pid] += sub_data['statistics']

    # 中央値計算
    prob_med = {}
    for pid, stat in prob_stat.items():
        if len(stat) == 0:
            prob_med[pid] = 1
        else:
            prob_med[pid] = stat[len(stat) // 2]
            if prob_med[pid] == 0:
                print('Warning: Median is 0.')
                prob_med[pid] = 1

    print('finish median analyze\nstart analyzing statistics')


    norm = make_stat_dict()
    no_norm = make_stat_dict()
    norm_sub = make_stat_dict() # ファイルサイズの中央値で正規化
    # 問題ごとのファイルサイズの統計情報取得
    psdb = ProblemStatDB()
    prob_size_stat = psdb.get_prob_stat_dict()

    # 統計情報を計算
    for i, userdata in enumerate(user_list):
        """
        中央値で割って正規化した個人の差分リストと，
        正規化していない差分リストを作成する
        その後，個人のデータを作成する
        """
        name = userdata['user_name']
        user_result = userdata['result']
        if (i + 1) % 100 == 0:
            print(i + 1)
        diff_list = []
        diff_list_norm = []
        diff_list_norm_sub = []

        # row = result_to_row(userdata, user_result)
        for sub_data in user_result:
            pid = sub_data['pid']
            pmed = prob_med[pid] / 100
            if pid in prob_size_stat:
                pmed_size = prob_size_stat[pid]['filesize_mean']
            else:
                pmed_size = -1
            for dist in sub_data['statistics']:
                if dist == 0:
                    continue
                diff_list.append(dist)
                diff_list_norm.append(dist / pmed)
                if pmed_size > 0:
                    diff_list_norm_sub.append(dist / pmed_size)


        add_statistics(diff_list, userdata['rating'], no_norm)
        add_statistics(diff_list_norm, userdata['rating'], norm)
        add_statistics(diff_list_norm_sub, userdata['rating'], norm_sub)


    # length = min(len(dist_high), len(dist_low), len(dist_mid))
    plot_statistics(norm, 'boxplot/normalized', ylim_data['norm'])
    plot_statistics(no_norm, 'boxplot/raw', ylim_data['no_norm'])
    plot_statistics(norm_sub, 'boxplot/normalized_filesize', ylim_data['norm_sub'])

    fdb.close()


def init_data_layer(base_layer):
    layers = [
        base_layer,
        ['norm_med', 'norm_file', 'raw'],
        stat_types,
        rating_split
    ]


if __name__ == '__main__':
    boxplot_dist()
