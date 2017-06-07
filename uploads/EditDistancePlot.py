import os
import json

import numpy as np

from boxplot import boxplot
from DistanceAnalyzer import rating_split, stat_types, stat_method

from acceptanceDB import AcceptanceDB
from problemDB import ProblemDB
from EditDistanceStatistics import EditDistanceStatisticsDB

def plot_statistics(data_list, path, file_name, ylim=None):
    """
    data_list: [{rating, diffs}]
    与えられたデータについて，個人ごとに[max, min, med, ...]を計算
    問題ごとに集計をとる
    結果を，path/method(maxなど)/file_nameにplotする
    """
    data_class = collect_statistics(data_list)
    for stype, data_list in data_class.items():
        save_path = path + stype + '/'
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        boxplot(
            data_list,
            label_vh=('edit distance', 'rating'),
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
    data_class = {}
    for stype in stat_types:
        data_class[stype] = [{'label': '-%d' % r, 'data': []} for r in rating_split]
    for user in data_list:
        for i, r in enumerate(rating_split):
            if user['rating'] >= r:
                continue
            for stype in stat_types:
                data_class[stype][i]['data'].append(stat_method(stype, user['diffs']))
            break
    return data_class


json_path = 'editdistance_statistics/json/'
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


def normalize_dataset(prob_stat: dict, edb: EditDistanceStatisticsDB):
    """
    問題の編集距離データが与えられるので，
    それらのdiffsの各値を，diffsの中央値(DBに計算済み)で割る
    """
    for prob in edb.select():
        prob_id = prob['problem_id']
        med = prob['median']
        if not prob_id in prob_stat:
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
            0.15, 0.25, 0.35, 0.45, 0.55, 0.8, 1.0
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
                return border
        return 1.0


def plot_editdistance_statistics(label_matcher, prob_stat, save_path):
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
        plot_statistics(stat, save_path, str(label) + '.png')


def editdistance_statistics(matcher, name):
    save_path = './editdistance_statistics/by_%s/' % name

    edb = EditDistanceStatisticsDB()
    raw = 'raw/'
    norm = 'norm/'
    prob_stat = load_prob_stat(edb)
    # plot_editdistance_statistics(matcher, prob_stat, save_path + raw)
    normalize_dataset(prob_stat, edb)
    plot_editdistance_statistics(matcher, prob_stat, save_path + norm)


if __name__ == '__main__':
    editdistance_statistics(AccLabel(), 'acc')
    editdistance_statistics(ScoreLabel(), 'score')
