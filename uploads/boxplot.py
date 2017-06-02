from matplotlib import pyplot as plt

def boxplot(data_list, label_vh=('', ''), ylim=None, path=None):
    """
    data_list: 辞書リスト
    {'label':'<label>', 'data':[data]}
    label_vh: タプルで縦横のラベル(縦, 横)
    ylim: yの範囲をリストで[下限, 上限]
          未指定なら[0, datamax]
    title: 保存パス
          未指定なら保存しないで表示
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    data = [d['data'] for d in data_list]
    label = [d['label'] for d in data_list]
    ax.boxplot(data)
    ax.set_xticklabels(label)
    plt.title('boxplot')
    plt.grid()
    plt.ylabel(label_vh[0])
    plt.xlabel(label_vh[1])
    if ylim:
        plt.ylim(ylim)
    if path:
        plt.savefig(path)
    else:
        plt.show()

def test():
    data = [
        {
            'label': 'math',
            'data': [1, 50, 48, 90, 4]
        },
        {
            'label': 'science',
            'data': [30, 20, 34, 50]
        }
    ]
    boxplot(data)

if __name__ == '__main__':
    test()
