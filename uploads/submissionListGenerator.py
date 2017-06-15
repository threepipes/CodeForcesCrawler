import time
from fileDB import FileDB
from fileDB_util import base_selection

lang_filter = set(['GNU C++14', 'GNU C++11', 'GNU C++'])


def append_dict(dic, key, value):
    if key not in dic:
        dic[key] = []
    dic[key].append(value)


def generate_submission_history_list(username: str, fdb: FileDB):
    """
    与えられたユーザに対して，
    提出履歴を問題ごと1行に並べて返す
    さらに，問題の順番もリストとして返す(順序的にはこちらが先)
    (lang_filterに属する言語のみ)
    """
    file_lists = {}
    file_where = ["user_name='%s'" % username] + base_selection
    file_data = list(fdb.select(where=file_where))
    for data in file_data:
        if data['timestamp'] is None:
            data['timestamp'] = -1
        else:
            data['timestamp'] = int(time.mktime(data['timestamp'].timetuple()))
    for data in sorted(file_data, key=lambda x: x['timestamp']):
        append_dict(file_lists, data['problem_id'], data)

    prob_id_list = []
    result = []
    for key, file_list in file_lists.items():
        prob_id_list.append(key)
        result.append(file_list)

    return prob_id_list, result


def extract_filenames(history_list: list, prefix=''):
    """
    history_listを，差分配列計算用に書き換えたものを返す
    具体的には，各行[{file_data}, ...]となっているのを，
    [<file_name>, ...]に書き直す
    """
    filename_list = []
    for histories in history_list:
        row = list(map(lambda fd: prefix + fd['file_name'], histories))
        filename_list.append(row)
    return filename_list


def get_history_list(username: str, fdb: FileDB, prefix=''):
    """
    あるユーザについて，問題ごと1行にファイル名を並べたリストを作成する
    prefixを指定することで，ファイルのパスを示す
    """
    pid_list, history_list = generate_submission_history_list(username, fdb)
    filename_list = extract_filenames(history_list, prefix=prefix)

    return pid_list, filename_list
