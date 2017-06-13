import os

import json
import numpy as np
from matplotlib import pyplot as plt

from fileDB import FileDB
from userDB import UserDB
from DistanceAnalyzer import analyze_user
from Database import Database


class EditDistanceStatisticsDB(Database):
    table_name = 'ProblemEditDistance'
    key = 'problem_id'
    column = [
        key,
        'max',
        'min',
        'mean',
        'median',
        'variance',
        'solver_rating_mean',
        'solver_rating_median',
    ]
    data_table = {
        key: 'VARCHAR(20)',
        'max': 'INT',
        'min': 'INT',
        'mean': 'DOUBLE',
        'median': 'INT',
        'variance': 'DOUBLE',
        'solver_rating_mean': 'DOUBLE',
        'solver_rating_median': 'INT',
    }

    def __init__(self):
        super(EditDistanceStatisticsDB, self).__init__(
            self.table_name,
            self.key,
            self.column,
            self.data_table
        )


def get_prob_data():
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
        rating = userdata['rating']
        print(name, i)

        for sub_data in user_result:
            pid = sub_data['pid']
            # for dist in sub_data['statistics']:
            if pid not in prob_stat:
                prob_stat[pid] = []
            stat = sub_data['statistics']
            prob_stat[pid].append({
                'rating': rating,
                'diffs': stat
            })
    return prob_stat


def get_statistics(data: list):
    sumup = []
    ratings = []
    for user in data:
        sumup += user['diffs']
        ratings.append(user['rating'])
    sumup = np.array(sumup)
    if len(sumup) == 0:
        return None, ratings
    return {
        'max': int(np.max(sumup)),
        'min': int(np.min(sumup)),
        'mean': float(np.mean(sumup)),
        'median': int(np.median(sumup)),
        'variance': float(np.var(sumup))
    }, ratings


def plot_rating_histogram(save_path, rating_list):
    """
    500スタートで100刻みで3000までプロット
    """
    plt.figure(figsize=(20, 20))
    plt.hist(rating_list, bins=100, range=(500, 3000))
    plt.ylim((0, 200))
    plt.savefig(save_path)
    plt.close()


def dump_json(save_path, dump_data):
    """
    編集距離等の統計情報をjsonファイルとして保存
    """
    with open(save_path, 'w') as f:
        json.dump(dump_data, f)


def main(edb):
    save_dir = 'editdistance_statistics/'
    json_dir = save_dir + 'json/'
    plot_dir = save_dir + 'rating/'
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
        os.mkdir(json_dir)
        os.mkdir(plot_dir)
    """
    編集距離リストなどのjsonデータ -> save_dir/json/prob_id
    回答者レーティングの度数分布プロット -> save_dir/rating/prob_id
    """
    prob_stat = get_prob_data()
    for pid, data in prob_stat.items():
        statistics, ratings = get_statistics(data)
        if not statistics:
            continue
        print('prob: ' + str(pid))
        statistics['problem_id'] = pid
        rating_list = np.array(ratings)
        statistics['solver_rating_mean'] = float(np.mean(rating_list))
        statistics['solver_rating_median'] = int(np.median(rating_list))
        edb.insert(statistics)
        edb.commit()
        plot_rating_histogram(plot_dir + str(pid) + '.png', rating_list)
        dump_json(json_dir + str(pid) + '.json', data)


def rating_statistics():
    from EditDistancePlot import load_prob_stat
    save_dir = 'editdistance_statistics/'
    plot_dir = save_dir + 'rating/'
    edb = EditDistanceStatisticsDB()
    prob_stat = load_prob_stat(edb, False)
    for pid, data in prob_stat:
        stat, ratings = get_statistics(data)
        rating_list = np.array(ratings)
        plot_rating_histogram(plot_dir + str(pid) + '.png', rating_list)


def init_db():
    edb = EditDistanceStatisticsDB()
    edb.init_table()
    return edb


"""
問題ごとの編集距離に関する統計をファイルに書き出す
"""

if __name__ == '__main__':
    rating_statistics()
