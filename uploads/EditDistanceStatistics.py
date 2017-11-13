import json
import os

import numpy as np

from database.Database import Database

col_list = [
    'levenshtein_distance',
    'add_node',
    'delete_node',
    'update_node',
    'move_node',
    'node_sum',
]

def_type = [
    ('min', 'INT'),
    ('max', 'INT'),
    ('mean', 'DOUBLE'),
    ('median', 'INT'),
    ('variance', 'DOUBLE'),
]


class EditDistanceStatisticsDB(Database):
    table_name = 'ProblemEditDistance'
    key = 'problem_id'

    def __init__(self):
        self.init_column()
        super(EditDistanceStatisticsDB, self).__init__(
            self.table_name,
            self.key,
            self.column,
            self.data_table
        )

    def init_column(self):
        column = [self.key]
        data_table = {
            self.key: 'VARCHAR(20)',
            'solver_rating_mean': 'DOUBLE',
            'solver_rating_median': 'INT',
        }
        for col in col_list:
            for tp in def_type:
                colname = col + '_' + tp[0]
                coltype = tp[1]
                column.append(colname)
                data_table[colname] = coltype
        column += [
            'solver_rating_mean',
            'solver_rating_median',
        ]
        self.column = column
        self.data_table = data_table


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


def get_prob_list(json_path):
    prob_list = []
    for file_name in os.listdir(json_path):
        prob_list.append(file_name.split('.')[0])
    return prob_list


base_path = './editdistance_statistics/json/'
def set_db(edb: EditDistanceStatisticsDB):
    column_list = col_list[:-1]
    prob_list = get_prob_list(base_path + column_list[0])
    for prob_id in prob_list:
        print(prob_id)
        ratings = None
        statistics = {}
        for col in column_list:
            path = base_path + col + '/%s.json' % prob_id
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
            stat, rat = get_statistics(data)
            if ratings is None:
                ratings = rat
            for tp in stat.keys():
                statistics[col + '_' + tp] = stat[tp]
        statistics['problem_id'] = prob_id
        ratings = np.array(ratings)
        statistics['solver_rating_mean'] = float(np.mean(ratings))
        statistics['solver_rating_median'] = int(np.median(ratings))
        edb.insert(statistics)


def init_db():
    edb = EditDistanceStatisticsDB()
    edb.init_table()
    return edb


def construct():
    edb = init_db()
    set_db(edb)


if __name__ == '__main__':
    construct()
