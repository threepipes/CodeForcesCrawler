import os
import json

import numpy as np

from boxplot import boxplot
from DistanceAnalyzer import rating_split, stat_types, stat_method

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
    """
    with open(json_path + str(pid) + '.json') as f:
        data = json.load(f)
    if empty_filter:
        data = list(filter(lambda x: x['diffs'], data))
    return data


def load_prob_stat(edb: EditDistanceStatisticsDB, empty_filter=True):
    for prob in edb.select():
        prob_id = prob['problem_id']
        if not os.path.exists(json_path + str(prob_id) + '.json'):
            continue
        yield prob_id, load(prob_id, empty_filter)


def normalize_dataset(prob_stat: dict, edb: EditDistanceStatisticsDB):
    for prob in edb.select():
        prob_id = prob['problem_id']
        med = prob['median']
        if not prob_id in prob_stat:
            continue
        for user in prob_stat[prob_id]:
            user['diffs'] = list(map(lambda x: x / med, user['diffs']))


def statistics_each_problem():
    edb = EditDistanceStatisticsDB()
    save_path = './editdistance_statistics/each_problem/'
    raw_path = save_path + 'raw/'
    norm_path = save_path + 'normalized/'
    prob_stat = {}
    for prob_id, stat in load_prob_stat(edb):
        prob_stat[prob_id] = stat
        # plot_statistics(stat, raw_path, prob_id + '.png')

    normalize_dataset(prob_stat, edb)
    for prob_id, stat in prob_stat.items():
        plot_statistics(stat, norm_path, prob_id + '.png')


def statistics_score():
    pass


if __name__ == '__main__':
    statistics_each_problem()
