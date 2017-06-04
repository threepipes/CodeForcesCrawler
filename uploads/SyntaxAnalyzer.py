import os
import sys

import numpy as np
from sklearn.manifold import MDS
from matplotlib import pyplot as plt

from Analyzer import Analyzer, AcceptedSubmissionFilter
from FileChooser import FileChooser
from userDB import UserSubmissionDB
from acceptanceDB import AcceptanceDB

colors = [
    ((120/255, 120/255, 120/255), 1200/2500),
    ((0, 120/255, 0), 1400/2500),
    ((0, 190/255, 190/255), 1600/2500),
    ((0, 0, 250/255), 1900/2500),
    ((170/255, 0, 250/255), 2200/2500),
    ((250/255, 200/255, 0), 2400/2500),
    ((250/255, 0, 0), 100)
]

class SyntaxAnalyzer(Analyzer):
    """
    文法的にソースコードをベクトル化し，距離を計測する
    FileChooserを設定し直すことで(reset)，
    新たなデータセットに対して測定できる(analyze)
    """

    def __init__(self, plot_file, file_chooser, command_dict):
        super(SyntaxAnalyzer, self).__init__(file_chooser)
        self.set_command_list(command_dict)
        self.plot_file = plot_file
        self.label_mapping()
        self.source_path = 'extracted/'
        self.y_lim = [-1, 1]
        self.x_lim = [-1, 1]

    def set_lim(self, lim):
        self.y_lim = self.x_lim = lim

    def set_plot_file(self, plot_file):
        self.plot_file = plot_file

    def write_list(self, file_list):
        with open(self.WORKING_DIR + self.LIST_FILE, 'w', encoding='utf-8') as f:
            for data in file_list:
                f.write(self.source_path + data['file_name'].replace('.src', '.cpp') + '\n')

    def label_mapping(self):
        """
        user_name -> 正答率 のマッピングを前計算しておく
        マッピングの対象はこのメソッドを変更することで可能
        """
        self.map_key = 'user_name'
        label_table = {}
        usdb = UserSubmissionDB()
        submission_data = usdb.select()
        for data in submission_data:
            label_table[data['user_name']] = data['acceptance_sample']
        self.label_table = label_table

    def to_label(self, file_data):
        """
        file_data -> label のマッピングを行う
        マッピングの辞書は，あらかじめ計算しておく
        """
        return '%1.2f' % self.label_table[file_data[self.map_key]]

    def to_color(self, file_data):
        """
        file_data -> color のマッピングを行う
        今回はlabelが[0-1]の実数なのでそれを使う
        """
        val = self.label_table[file_data[self.map_key]]
        for col in colors:
            if val < col[1] / 2:
                return col[0]
        return (0, 0, 0)

    def output(self, file_list, data):
        """
        MDSを用いて2次元plotし，pngとして出力する
        (file_list -> label のマッピングはto_labelで)
        -> 今回はfile_list -> color のマッピングを行う
        """
        dist = np.matrix(data)
        mds = MDS(n_components=2, dissimilarity='precomputed')
        pos = mds.fit_transform(dist)

        plt.figure(figsize=(30, 30))
        plt.scatter(
            pos[:, 0],
            pos[:, 1],
            c=['w' for _ in file_list] # [self.to_color(f) for f in file_list]
        )
        for p, file_data in zip(pos, file_list):
            col = self.to_color(file_data)
            label = self.to_label(file_data)
            plt.text(p[0], p[1], label, fontdict={'size':9, 'color':col})
        plt.ylim(*self.y_lim)
        plt.xlim(*self.x_lim)
        plt.savefig(self.plot_file)


def get_test_chooser():
    column = 'problem_id'
    key_list = [
        '101A',
    ]
    chooser = FileChooser(column)
    chooser.set_key_list(key_list)
    return chooser


def test():
    chooser = get_test_chooser()
    command_dict = {
        'task': 'dist',
        'method': 'syntax'
    }
    al = SyntaxAnalyzer('plot.png', chooser, command_dict)
    al.analyze()


def get_plot_dir(dir_name):
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    return dir_name


def analyze_many_solved(analyzer, command_dict, plot_dir, lim):
    """
    command_dict (ex.): {
        'task': 'dist',
        'method': 'syntax'
    }
    plot_dir (ex.): 'data_plot_ngram_acc_2'
    """
    acc_db = AcceptanceDB()
    prob_list = acc_db.select()
    column = 'problem_id'
    chooser = FileChooser(column)
    al = analyzer('plot.png', chooser, command_dict)
    al.set_lim(lim)
    dir_name = get_plot_dir(plot_dir)
    count = 0
    file_filter = AcceptedSubmissionFilter(UserSubmissionDB())
    for prob in prob_list:
        if int(prob['solved_in_sample']) < 1000:
            continue
        print(prob)
        key = [prob[column]]
        chooser.set_key_list(key)
        al.set_plot_file('%s/%s.png' % (dir_name, prob[column]))
        al.analyze(file_filter)

        count += 1
        if count >= 20:
            break

if __name__ == '__main__':
    usage = """
    引数に，使うコード分析手法と色の基準と図の置き場を設定する
    解析器: syntax or ngram
    色の基準: acc or rating
    コマンド例: python SyntaxAnalyzer.py method=syntax base=acc plot=acc_synt
    """
    if len(sys.argv) != 4:
        print(usage)
        sys.exit()
    option = {}
    for arg in sys.argv[1:]:
        spl = arg.split('=')
        option[spl[0]] = spl[1]

    # syntax -> task:dist, method:syntax
    # ngram -> task:ngram, n:1
    if option['method'] == 'syntax':
        command_dict = {
            'task': 'dist',
            'method': 'syntax'
        }
    elif option['method'] == 'ngram':
        command_dict = {
            'task': 'ngram',
            'n': 1
        }
    else:
        print('Method specifing error.')
        sys.exit()
    if option['base'] == 'acc':
        analyzer_class = SyntaxAnalyzer
        lim = [-0.5, 0.5]
    else:
        from SyntaxAnalyzerWithRating import SyntaxAnalyzerWithRating
        analyzer_class = SyntaxAnalyzerWithRating
        lim = [-0.1, 0.1]

    analyze_many_solved(analyzer_class, command_dict, option['plot'], lim)
