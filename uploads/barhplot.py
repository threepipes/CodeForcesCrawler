import matplotlib.pyplot as plt
import numpy as np


def barh_plot_m2(multiset2: dict, bar_order: list, title='sample', path=None):
    """
    multiset2: [key][tag] = 個数
    bar_order: name, colorを含む情報
    """
    frequency = []
    for key, ms in multiset2.items():
        freq = 0
        for v in ms.values():
            freq += v
        frequency.append((freq, key))

    y = [[] for _ in bar_order]
    tags = []
    for _, key in sorted(frequency, key=lambda x: x[0]):
        ms = multiset2[key]
        tags.append(key)
        for i, tag_info in enumerate(bar_order):
            name = tag_info['name']
            if name not in ms:
                y[i].append(0)
            else:
                y[i].append(ms[name])

    y = [np.array(row) for row in y]
    y_sum = np.zeros_like(y[0])
    x = np.arange(len(y[0]))

    fig = plt.figure(figsize=(20, 15))
    ax = fig.add_subplot(111)

    for i, y_data in enumerate(y):
        ax.barh(
            x, y_data, color=bar_order[i]['color'],
            left=y_sum, align='center'
        )
        y_sum += y_data
    plt.yticks(x, tags)
    plt.title(title)

    if path:
        plt.savefig(path)
        plt.close()
    else:
        plt.show()
