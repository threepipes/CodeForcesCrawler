from subprocess import *
import random
import json
import sys
import os
import shutil
from fileDB import FileDB
from userDB import UserDB
from problemDB import ProblemDB
from acceptanceDB import AcceptanceDB

import numpy as np
from sklearn.manifold import MDS
from matplotlib import pyplot as plt


base_dir = 'C:/Work/Python/Lab/CodeForcesCrawler/data/extracted/'
jar_path = 'analyze.jar'

def plot(data, labels, filename):
    plt.figure(figsize=(12, 12))
    plt.scatter(data[:, 0], data[:, 1], c=["w" for _ in labels])
    for d, l in zip(data, labels):
        col = min(1, l / 2500)
        plt.text(d[0], d[1], str(l), fontdict={"size":12, 'color':(1-col, col, 1-col, 1)})
    plt.savefig(filename)

def analyze(jar_path, n):
    cmd = ['java', '-jar', jar_path, '--ngram', str(n), out_file]
    pipe = Popen(cmd, cwd='../data', stdout=PIPE, stderr=None).stdout
    result = []
    for line in pipe.readlines():
        data = json.loads(line.decode('utf-8').strip())
        result.append(data)
    print('finish analyze.')
    return result


def get_filedata_list(prob_id):
    file_db = FileDB()
    where = {
        'problem_id': prob_id,
        'verdict': 'OK',
        'lang': 'GNU C++11',
    }
    file_list = file_db.select(where=where, limit=300)
    return file_list


def choose_prob_id():
    return '727A'


out_file = 'file_list.txt'
def write_filelist(file_list):
    with open('../data/' + out_file, 'w') as f:
        for filedata in file_list:
            f.write(base_dir + filedata['file_name'].replace('.src', '.cpp') + '\n')


def get_ratings(file_list):
    user_db = UserDB()
    rating = {}
    for user in user_db.select():
        rating[user['user_name']] = user['rating']
    rating_list = []
    for filedata in file_list:
        rating_list.append(rating[filedata['user_name']])
    return rating_list


def plot_data(dist, labels, filename):
    data = np.matrix(dist)
    mds = MDS(n_components=2, dissimilarity='precomputed')
    pos = mds.fit_transform(data)
    plot(pos, labels, filename)


def copy_sources(file_list, save_path, ratings):
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    for rate, filedata in zip(ratings, file_list):
        name = filedata['file_name']
        shutil.copyfile(base_dir + name, save_path + '/' + str(rate) + '_' + name)


def analyze_prob(prob_id):
    path = 'data_plot/' + prob_id + '/'
    if not os.path.exists(path):
        os.mkdir(path)
    filepref = path + 'plot'
    file_list = get_filedata_list(prob_id)
    write_filelist(file_list)
    ratings = get_ratings(file_list)
    # copy_sources(file_list, filepref, ratings)

    for i in range(4):
        ngram = i + 1
        filename = filepref + '_' + str(ngram) + '.png'
        dist = analyze(jar_path, ngram)
        plot_data(dist, ratings, filename)

def only_getting_sources(prob_id):
    file_list = get_filedata_list(prob_id)
    ratings = get_ratings(file_list)
    save_path = 'data/source_%s' % prob_id
    copy_sources(file_list, save_path, ratings)


if __name__ == '__main__':
    # if len(sys.argv) > 1:
    #     filepref = sys.argv[1]
    # else:
    #     filepref = 'plot_tmp'
    # filepref = 'data/' + filepref

    acc_db = AcceptanceDB()
    prob_list = acc_db.select()
    for prob in prob_list:
        if int(prob['solved_in_sample']) < 500:
            continue
        print(prob)
        analyze_prob(prob['problem_id'])
