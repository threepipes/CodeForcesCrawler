"""
SubmissionHistoryDBの各列をEditDistancePlot#loadで読み込める形式に変換する
保存先は"/editdistance_statistics/json/<column_name>/<prob_id>.json"
"""
import json
import os

from fileDB import FileDB
from userDB import UserDB
from problemDB import ProblemDB, ProblemStatDB
from submissionHistoryDB import SubmissionHistoryDB

from userDB_util import generate_dict
from fileDB_util import base_selection

lang_list = ['GNU C++14', 'GNU C++11', 'GNU C++']
lang_select = '(%s)' % ' or '.join(['lang=' + lang for lang in lang_list])
sdb_col_list = SubmissionHistoryDB.column[3:]
save_path_base = './editdistance_statistics/json/'


def get_submissions(prob_id: str, fdb: FileDB):
    return fdb.select(where=(["problem_id='%s'" % prob_id] + base_selection))


def get_data_dict():
    data_dict = {}
    for col in sdb_col_list:
        data_dict[col] = {}
    return data_dict


def filename_to_username(file_name: str):
    spl = file_name.split('_')
    suf_len = len(spl[-1]) + len(spl[-2])
    return file_name[:-suf_len - 2]


def add_data(
        data_dict: dict,
        file_data: dict,
        sdb: SubmissionHistoryDB,
        users: dict):
    file_name = file_data['file_name']
    diff_data = list(sdb.select(where={'file_name': file_name}))
    if len(diff_data) == 0:
        return
    diff_data = diff_data[0]
    if diff_data['next_file'] == '-':
        return
    user_name = filename_to_username(file_name)
    rating = users[user_name]['rating']
    for col, col_data in data_dict.items():
        if user_name not in col_data:
            col_data[user_name] = {'rating': rating, 'diffs': []}
        diffs = col_data[user_name]['diffs']
        diffs.append(diff_data[col])


def generate_diff_file(data_dict: dict, prob: dict):
    for col, col_data in data_dict.items():
        save_path = save_path_base + '%s/%s.json' % (col, prob['problem_id'])
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(list(data_dict[col].values()), f)


def transport_db_to_json():
    udb = UserDB()
    user_dict = generate_dict(udb)
    pdb = ProblemStatDB()
    fdb = FileDB()
    sdb = SubmissionHistoryDB()

    for col in sdb_col_list:
        if not os.path.exists(save_path_base + col):
            os.makedirs(save_path_base + col)

    for prob in pdb.select(where='filesize_max_c>0'):
        """
        column -> user_name -> {rating: int, diffs: list}
        と指定できる辞書上にデータを構築していく
        """
        print(prob['problem_id'])
        data_dict = get_data_dict()
        count = 0
        for sub in get_submissions(prob['problem_id'], fdb):
            add_data(data_dict, sub, sdb, user_dict)
            count += 1
        if count == 0:
            continue
        generate_diff_file(data_dict, prob)
        break


def test_filename2user():
    test_name = [
        '12_09_21042636_721.src',
        '11_sub_21151321_723.src',
        '1200rohit_18554706_682.src'
    ]
    for name in test_name:
        print(filename_to_username(name))


if __name__ == '__main__':
    transport_db_to_json()
