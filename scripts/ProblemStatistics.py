"""
問題に関する統計をとるためのスクリプト
例: 問題の平均ファイルサイズと平均編集距離の相関
"""

from matplotlib import pyplot as plt

from Database import Database
from EditDistanceStatistics import EditDistanceStatisticsDB
from acceptanceDB import AcceptanceDB
from problemDB import ProblemDB, ProblemStatDB


def update_info(prob_info: dict, db: Database, filtering=None):
    for prob in db.select():
        if filtering and not filtering(prob):
            continue
        pid = prob['problem_id']
        if pid not in prob_info:
            prob_info[pid] = {'count': 1}
        else:
            prob_info[pid]['count'] += 1
        prob_info[pid].update(prob)


def get_problem_info():
    """
    問題の各情報を結合したデータを返す
    欠損値が存在することに注意
    """
    edb = EditDistanceStatisticsDB()
    adb = AcceptanceDB()
    pdb = ProblemDB()
    psdb = ProblemStatDB()
    prob_info = {}
    update_info(prob_info, edb, lambda x: x['mean'] < 400)
    update_info(prob_info, adb)
    update_info(prob_info, pdb)
    update_info(prob_info, psdb, lambda x: x['filesize_mean'] < 20000)
    edb.close()
    adb.close()
    pdb.close()
    psdb.close()

    return prob_info


def plot_data(prob_info: dict, key_x: str, key_y: str, save_path: str):
    """
    各問題を頂点，key_xが表す要素を横軸，key_yが表す要素を縦軸とし，
    2次元平面上に散布図をplotする
    """
    x = []
    y = []
    label = []
    for pid, prob in prob_info.items():
        if key_x not in prob or key_y not in prob:
            continue
        label.append(pid)
        x.append(prob[key_x])
        y.append(prob[key_y])
    plt.figure(figsize=(20, 20))
    plt.ylabel(key_y)
    plt.xlabel(key_x)
    # plt.scatter(x, y, c=['w' for _ in x])
    plt.scatter(x, y)
    # for i in range(len(label)):
    #     plt.text(x[i], y[i], label, fontdict={'size': 9, 'color': (0, 0, 1)})
    plt.savefig(save_path)
    plt.close()


def plot_problem_statistics():
    path = './problem_info/'
    prob_info = get_problem_info()
    print('finish getting info')
    acc_rate = 'acceptance_rate'
    score = 'points'
    edit_med = 'median'
    edit_mean = 'mean'
    rating_med = 'solver_rating_median'
    rating_mean = 'solver_rating_mean'
    fs_med = 'filesize_median'
    fs_mean = 'filesize_mean'
    label = [
        acc_rate,
        score,
        edit_mean,
        edit_med,
        rating_mean,
        rating_med,
        fs_mean,
        fs_med
    ]
    for i in range(len(label)):
        for j in range(i + 1, len(label)):
            print('generating %s and %s' % (label[i], label[j]))
            plot_data(prob_info, label[i], label[j], path + '%s_%s.png' % (label[i], label[j]))

if __name__ == '__main__':
    plot_problem_statistics()
