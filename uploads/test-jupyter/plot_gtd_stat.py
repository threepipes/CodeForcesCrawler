import os
import pandas as pd
from matplotlib import pyplot as plt
from logging import getLogger, INFO

logger = getLogger(__file__)
logger.setLevel(INFO)


def save_barh(df, name, figsize=(10, 120)):
    logger.info('saving file: ' + name)
    figure = df.plot.barh(stacked=True, figsize=figsize).get_figure()
    figure.subplots_adjust(left=0.2)
    figure.savefig(name)
    figure.clf()
    plt.clf()
    plt.close()


def plot_df(basename, label, srs, top=20, ext='png'):
    df = srs.unstack().fillna(0)
    indexer = df.sum(1).argsort()
    sorted_df = df.take(indexer)
    save_barh(sorted_df.tail(20), basename + '_top20_sorted_%s.%s' % (label, ext), figsize=(10, 10))
    save_barh(sorted_df, basename + '_sorted_%s.%s' % (label, ext), figsize=(10, 120))
    save_barh(df, basename + '_%s.%s' % (label, ext), figsize=(10, 120))


def set_dir(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    return dirname


def plot_stat(side, prefix=''):
    logger.info('starting %s side' % side)
    div_norm = pd.read_csv('dived_%s_gp_norm.csv' % side,
                           index_col=[0], header=[0, 1, 2, 3],
                           skipinitialspace=True, tupleize_cols=True)
    div_norm.columns = pd.MultiIndex.from_tuples(div_norm.columns)
    acc_group = div_norm.sum(axis=1, level=[0, 1, 2])

    savedir = set_dir('plot/%s_each_acc_div%s/' % (prefix, side))
    for index, row in acc_group.iterrows():
        plot_df(savedir + 'acc', '%3s' % str(index), row)

    savedir = set_dir('plot/%s_each_rating_div%s/' % (prefix, side))
    for rating, srs in div_norm.sum().groupby(level=3, group_keys=False):
        srs.index = srs.index.droplevel(3)
        label = rating.replace(' ', '')
        plot_df(savedir + 'rating', label, srs)

    savedir = 'plot/%s_each_rating_acc_div%s/' % (prefix, side)
    basename = savedir + 'acc_rating'
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    for acc, row in div_norm.iterrows():
        for rating, srs in row.groupby(level=3):
            srs.index = srs.index.droplevel(3)
            label = '%s_%.2f' % (rating.replace(' ', ''), acc)
            plot_df(basename, label, srs)


# plot_stat('user', 'onlycond')
plot_stat('file', 'onlycond')
