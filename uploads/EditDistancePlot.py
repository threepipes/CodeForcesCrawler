import os
import json

import numpy as np
from joblib import Parallel, delayed
from scipy.stats import pearsonr

from boxplot import boxplot
from DistanceAnalyzer import rating_split, stat_types, stat_method

from acceptanceDB import AcceptanceDB
from problemDB import ProblemDB
from EditDistanceStatistics import EditDistanceStatisticsDB
from statistics2D import barplot


def set_correlation_data(info, corr_list, p_list, labels):
    cols = ['diff', 'prob_div', 'norm', 'label']
    data_path = './correlation/'

    if not os.path.exists(data_path):
        os.mkdir(data_path)
    data_path += 'corr.csv'
    print(info)

    with open(data_path, 'a') as f:
        for i, label in enumerate(labels):
            row = ''
            for col in cols:
                row += info[col] + ','
            row += label + ','
            row += str(corr_list[i]) + ','
            if p_list[i] < 0.05:
                row += 'sgn'
            f.write(row + '\n')


def get_correlation(data_list, path, file_name, ylim=None, info=None):
    """
    data_list: [{rating: int, diffs: list}]
    -> {
        max: {x:[rating], y:[diff_max]},
        min: {x:[rating], y:[diff_min]},
        ...
    }
    に変換した後，相関係数を計算する
    TODO 検定
    TODO 散布図のplot
    """
    data_points = collect2points(data_list)
    corr_list = []
    p_list = []
    if not os.path.exists(path):
        os.makedirs(path)
    for stype, data_list in data_points.items():
        corr, p = pearsonr(data_list['x'], data_list['y'])
        corr_list.append(corr)
        p_list.append(p)
    # if info:
    #     set_correlation_data(info, corr_list, p_list, stat_types)
    barplot(corr_list, stat_types, path + 'corr_' + file_name, ylim=(-1, 1))
    barplot(p_list, stat_types, path + 'p_' + file_name, ylim=(0, 0.1))


def collect2points(data_list: list):
    """
    data_list: [{rating: int, diffs: list}]
    -> {
        max: {x:[rating], y:[diff_max]},
        min: {x:[rating], y:[diff_min]},
        ...
    }
    """
    data_class = {}
    for stype in stat_types:
        data_class[stype] = {'x': [], 'y': []}
    for user in data_list:
        for stype in stat_types:
            data_class[stype]['x'].append(user['rating'])
            data_class[stype]['y'].append(stat_method(stype, user['diffs']))
    return data_class


def plot_statistics(data_list, path, file_name, ylim=None):
    """
    data_list: [{rating: int, diffs: list}]
    与えられたデータについて，個人ごとに[max, min, med, ...]を計算
    問題ごとに集計をとる
    結果を，path/method(maxなど)/file_nameにplotする
    """
    data_class = collect_statistics(data_list)
    for stype, data_list in data_class.items():
        save_path = path + stype + '/'
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        print('saving : ' + path)
        boxplot(
            data_list,
            label_vh=('Normalized Levenshtein Distance', 'Rating'),
            ylim=ylim,
            path=save_path + file_name
        )


def collect_statistics(data_list: list):
    """
    [{rating: int, diffs: list}]で与えられるdata_listを，
    {
        max: [{label: str, data: list}],
        min: [同上],
        ...
    }
    という形式に変更する．
    内部のリストは，さらにレーティングによって分類されており，
    ラベルがレーティング帯を表す
    """
    rating_label = [
        '0 - 1100', '1101 - 1200', '1201 - 1300', '1301 - 1400', '1401 - 1500',
        '1501 - 1600', '1601 - 1700', '1701 - 1900', '1901 - 2200', '2200 - 4000'
    ]
    data_class = {}
    for stype in stat_types:
        data_class[stype] = [{'label': r, 'data': []} for r in rating_label]
    for user in data_list:
        for i, r in enumerate(rating_split):
            if user['rating'] >= r:
                continue
            for stype in stat_types:
                data_class[stype][i]['data'].append(stat_method(stype, user['diffs']))
            break
    return data_class


base_json_path = 'editdistance_statistics/json/'
json_path = ''
def load(pid, empty_filter=True):
    """
    [{'rating': int, 'diffs': []}]
    を指定されたproblem_idについて読み込む．
    empty_filterを指定すると，diffsが空のものを除外する
    """
    with open(json_path + str(pid) + '.json') as f:
        data = json.load(f)
    if empty_filter:
        data = list(filter(lambda x: x['diffs'], data))
    return data


def load_prob_stat(edb: EditDistanceStatisticsDB, empty_filter=True):
    """
    すべての問題の編集距離データをloadする
    {problem_id: [{rating: int, diffs: list}]}
    を返す
    """
    prob_stat = {}
    for prob in edb.select():
        prob_id = prob['problem_id']
        if not os.path.exists(json_path + str(prob_id) + '.json'):
            continue
        prob_stat[prob_id] = load(prob_id, empty_filter)
    return prob_stat


def normalize_dataset(prob_stat: dict, edb: EditDistanceStatisticsDB, group: str):
    """
    問題の編集距離データが与えられるので，
    それらのdiffsの各値を，diffsの中央値(DBに計算済み)で割る
    """
    for prob in edb.select():
        prob_id = prob['problem_id']
        med = prob[group + '_mean']
        if med == 0:
            med = 0.001
        if prob_id not in prob_stat:
            continue
        for user in prob_stat[prob_id]:
            user['diffs'] = list(map(lambda x: x / med, user['diffs']))


def statistics_each_problem():
    """
    問題個別に編集距離の統計データをplotする
    """
    edb = EditDistanceStatisticsDB()
    save_path = './editdistance_statistics/each_problem/'
    raw_path = save_path + 'raw/'
    norm_path = save_path + 'normalized/'
    prob_stat = {}
    for prob_id, stat in load_prob_stat(edb):
        prob_stat[prob_id] = stat
        plot_statistics(stat, raw_path, prob_id + '.png')

    normalize_dataset(prob_stat, edb)
    for prob_id, stat in prob_stat.items():
        plot_statistics(stat, norm_path, prob_id + '.png')


class ScoreLabel:
    def __init__(self):
        self.score_dict = self.get_score_dict()

    def get_score_dict(self):
        valid_score = [(x + 1) * 500 for x in range(6)]
        pdb = ProblemDB()
        prob_dict = {}
        for prob in pdb.select(['problem_id', 'points']):
            sc = prob['points']
            if sc not in valid_score:
                continue
            prob_dict[prob['problem_id']] = sc
        return prob_dict

    def to_label(self, pid):
        if pid not in self.score_dict:
            return None
        return self.score_dict[pid]


class AccLabel:
    def __init__(self):
        self.acc_split = [
            0.2 * (x + 1) for x in range(5)
        ]
        self.acc_dict = self.get_acc_dict()

    def get_acc_dict(self):
        acdb = AcceptanceDB()
        acc_dict = {}
        for prob in acdb.select(['problem_id', 'acceptance_rate']):
            acc = prob['acceptance_rate']
            acc_dict[prob['problem_id']] = acc
        return acc_dict

    def to_label(self, pid):
        if pid not in self.acc_dict:
            return None
        acc = self.acc_dict[pid]
        for border in self.acc_split:
            if acc <= border:
                return '%1.2f' % border
        return 1.0


def plot_editdistance_statistics(label_matcher, prob_stat, save_path, info=None):
    """
    problem_id -> labelに変換するmatcherを与える
    これに基づいて問題を分類し，分類ごとに統計データをplotする
    """
    prob_stat_labeled = {}
    for prob_id, stat in prob_stat.items():
        label = label_matcher.to_label(prob_id)
        if not label:
            continue
        if label not in prob_stat_labeled:
            prob_stat_labeled[label] = []
        prob_stat_labeled[label] += stat

    for label, stat in prob_stat_labeled.items():
        """
        plot手法についてここで選択
        現在:
         - plot_statistics: boxplot
         - get_correlation: 相関と検定
        """
        plot_statistics(stat, save_path, str(label) + '.png')
        # if info:
        #     info['label'] = str(label)
        # get_correlation(stat, save_path, str(label) + '.png', info=info)


def editdistance_statistics(matcher, group, name):
    global json_path, base_json_path
    json_path = base_json_path + group + '/'
    save_path = './editdistance_statistics/plot/%s/by_%s/' % (group, name)

    edb = EditDistanceStatisticsDB()
    raw = 'raw/'
    norm = 'norm/'
    info = {'diff': group, 'prob_div': name, 'norm': 'raw'}
    prob_stat = load_prob_stat(edb)
    # plot_editdistance_statistics(matcher, prob_stat, save_path + raw, info=info)
    info['norm'] = 'norm'
    normalize_dataset(prob_stat, edb, group)
    plot_editdistance_statistics(matcher, prob_stat, save_path + norm, info=info)


def statistics_group(group: str):
    editdistance_statistics(AccLabel(), group, 'acc')
    # editdistance_statistics(ScoreLabel(), group, 'score')


if __name__ == '__main__':
    from submissionHistoryDB import SubmissionHistoryDB
    groups = SubmissionHistoryDB.column[4:-1]
    statistics_group('levenshtein_distance')
    # for g in groups:
    #     statistics_group(g)
    # print(groups)
    # Parallel(n_jobs=len(groups)*2, verbose=10)(
    #     delayed(statistics_group)(g) for g in groups
    # )
