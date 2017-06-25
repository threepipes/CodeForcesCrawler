from Database import Database


class ProblemDB(Database):
    table_name = 'Problem'
    key = 'problem_id'
    column = [
        'problem_id',
        'prob_index',
        'competition_id',
        'points'
    ]
    data_table = {
        'problem_id': 'VARCHAR(20)',
        'prob_index': 'VARCHAR(5)',
        'competition_id': 'INT(10)',
        'points': 'INT(5)'
    }

    def __init__(self):
        super(ProblemDB, self).__init__(self.table_name, self.key, self.column, self.data_table)


class ProblemStatDB(Database):
    table_name = 'ProblemStatistics'
    key = 'problem_id'
    column = [
        key,
        'filesize_max',
        'filesize_min',
        'filesize_mean',
        'filesize_median',
        'filesize_variance',
        'filesize_max_c',
        'filesize_min_c',
        'filesize_mean_c',
        'filesize_median_c',
        'filesize_variance_c',
    ]
    data_table = {
        key: 'VARCHAR(20)',
        'filesize_max': 'INT',
        'filesize_min': 'INT',
        'filesize_mean': 'DOUBLE',
        'filesize_median': 'INT',
        'filesize_variance': 'DOUBLE',
        'filesize_max_c': 'INT',
        'filesize_min_c': 'INT',
        'filesize_mean_c': 'DOUBLE',
        'filesize_median_c': 'INT',
        'filesize_variance_c': 'DOUBLE',
    }

    def __init__(self):
        super(ProblemStatDB, self).__init__(self.table_name, self.key, self.column, self.data_table)

    def get_prob_stat_dict(self):
        result = {}
        for row in self.select():
            result[row[self.key]] = row
        return result


def score_graph():
    path = './problem_info/'
    pdb = ProblemDB()
    scores = {}
    for prob in pdb.select():
        sc = prob['points']
        if sc is None:
            sc = -1
        if sc not in scores:
            scores[sc] = 0
        scores[sc] += 1

    from matplotlib import pyplot as plt

    x = []
    y = []
    label = []
    for i, key in enumerate(sorted(scores.keys())):
        x.append(i)
        y.append(scores[key])
        label.append(str(key))

    plt.figure(figsize=(30, 8))
    plt.bar(x, y, align='center')
    plt.xticks(x, label)
    plt.savefig(path + 'score_distribution.png')
    plt.close()


if __name__ == '__main__':
    score_graph()
