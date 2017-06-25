import os.path
import numpy as np

from problemDB import ProblemDB, ProblemStatDB
from fileDB import FileDB

def init_prob_stat():
    psdb = ProblemStatDB()
    psdb.init_table()
    return psdb

def generate_prob_stat():
    psdb = init_prob_stat()
    pdb = ProblemDB()
    fdb = FileDB()

    problem_id = 'problem_id'
    src_dir = '../data/src/'

    for prob in pdb.select():
        pid = prob[problem_id]
        size_list = []
        size_list_c = []
        for submission in fdb.select(where={problem_id: pid, 'verdict': 'OK'}):
            file_name = submission['file_name']
            size = os.path.getsize(os.path.join(src_dir, file_name))
            size_list.append(size)
            if submission['during_competition']:
                size_list_c.append(size)

        if not size_list:
            size_list.append(0)
        if not size_list_c:
            size_list_c.append(0)

        size_list = np.array(size_list)
        size_list_c = np.array(size_list_c)

        insert_data = {
            problem_id: pid,
            'filesize_max': int(np.max(size_list)),
            'filesize_min': int(np.min(size_list)),
            'filesize_mean': float(np.mean(size_list)),
            'filesize_median': int(np.median(size_list)),
            'filesize_variance': float(np.var(size_list)),
            'filesize_max_c': int(np.max(size_list_c)),
            'filesize_min_c': int(np.min(size_list_c)),
            'filesize_mean_c': float(np.mean(size_list_c)),
            'filesize_median_c': int(np.median(size_list_c)),
            'filesize_variance_c': float(np.var(size_list_c)),
        }

        psdb.insert(insert_data)
        psdb.commit()

if __name__ == '__main__':
    generate_prob_stat()