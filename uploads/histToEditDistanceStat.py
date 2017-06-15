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

from userDB_util import get_user
from fileDB_util import get_file

lang_list = ['GNU C++14', 'GNU C++11', 'GNU C++']
lang_select = '(%s)' % ' or '.join(['lang=' + lang for lang in lang_list])
sdb_col_list = SubmissionHistoryDB.column[3:]
save_path_base = './editdistance_statistics/json/'


def get_submissions(prob_id: str, sdb: SubmissionHistoryDB):
    return sdb.select(where=({'problem_id': prob_id}))


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
        diff_data: dict,
        user_data: dict):
    file_name = file_data['file_name']
    if diff_data['next_file'] == '-':
        return
    rating = user_data['rating']
    for col, col_data in data_dict.items():
        if user_name not in col_data:
            col_data[user_name] = {'rating': rating, 'diffs': []}
        diffs = col_data[user_name]['diffs']
        diffs.append(diff_data[col])


def generate_diff_file(data_dict: dict, prob_id: str):
    for col, col_data in data_dict.items():
        save_path = save_path_base + '%s/%s.json' % (col, prob_id)
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(list(data_dict[col].values()), f)


def get_submission_chain(sub_list: list, fdb: FileDB):
    has_ac = False
    chain = []
    for sub in sub_list:
        file_data = get_file(sub['file_name'], fdb)
        chain.append((sub, file_data))
        if file_data['verdict'] == 'OK' and file_data['during_competition']:
            return chain
    return []


def set_diff_file(prob_id: str):
    sdb = SubmissionHistoryDB()
    fdb = FileDB()
    udb = UserDB()

    data_dict = get_data_dict()
    count = 0
    sub_list = []
    for sub in get_submissions(prob['problem_id'], sdb):
        sub_list.append(sub)
        if sub['next_file'] != '-':
            continue
        sub_chain = get_submission_chain(sub_list, fdb)
        if len(sub_chain) < 2:
            continue
        user_data = get_user(sub_chain[0][1]['user_name'], udb)
        for diff_data, file_data in sub_chain[:-1]:
            add_data(data_dict, file_data, diff_data, user_data)
            count += 1

    sdb.close()
    fdb.close()
    udb.close()
    if count == 0:
        return
    generate_diff_file(data_dict, prob)


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
        set_diff_file(prob['problem_id'])


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
