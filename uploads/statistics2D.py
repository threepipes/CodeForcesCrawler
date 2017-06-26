"""
x:[...], y:[...]
と渡されるものについて，統計・プロットを行う
"""
from scipy.stats import pearsonr
import matplotlib.pyplot as plt


def barplot(data: list, label: list, save_path: str, ylim=None):
    x = list(range(1, len(data) + 1))
    positive = []
    negative = []
    for d in data:
        if d >= 0:
            positive.append(d)
            negative.append(0)
        else:
            positive.append(0)
            negative.append(d)
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111)
    ax.bar(x, positive, tick_label=label, align='center', color='b')
    ax.bar(x, negative, tick_label=label, align='center', color='r')
    plt.title(save_path)
    if ylim:
        plt.ylim(ylim)
    plt.savefig(save_path)
    plt.close()


def test_barplot():
    data = [1, 2, 3, 4, 5]
    label = 'a,b,c,d,e'.split(',')
    save_path = './file.png'
    barplot(data, label, save_path)


def calc_2D_stat(data: dict):
    """
    現在計算するもの(追加予定)
    - 相関係数
    - 相関の検定結果
    """
    corr, p = pearsonr(data['x'], data['y'])
    print('相関係数 r = {r}'.format(r=corr))
    print('有意確率 p = {p}'.format(p=p))
    print('有意確率 p > 0.05: {result}'.format(result=(p > 0.05)))


def get_mouse_data():
    mouse = """940	920
880	910
720	850
840	880
1020	970
690	960
920	990
850	760
710	900
980	940"""
    x = []
    y = []
    for m in mouse.split('\n'):
        a, b = map(int, m.split())
        x.append(a)
        y.append(b)
    return {'x': x, 'y': y}


def get_simple_data():
    x = [1, 2, 3, 4, 5]
    y = [0, 2, 4, 5, 8]
    return {'x': x, 'y': y}


def test_calc_2D_stat():
    print('simple_data')
    calc_2D_stat(get_simple_data())
    print('\nmouse_data')
    calc_2D_stat(get_mouse_data())


if __name__ == '__main__':
    test_barplot()
