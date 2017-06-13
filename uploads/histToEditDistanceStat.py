"""
SubmissionHistoryDBの各列をEditDistancePlot#loadで読み込める形式に変換する
保存先は"/editdistance_statistics/json/<column_name>/<prob_id>.json"
"""
from fileDB import FileDB
from userDB import UserDB
from problemDB import ProblemDB
from submissionHistoryDB import SubmissionHistoryDB

from userDB_util import generate_dict

lang_list = ['GNU C++14', 'GNU C++11', 'GNU C++']
lang_select = '(%s)' % ' or '.join(['lang=' + lang for lang in lang_list])


def get_submissions(prob_id: str, fdb: FileDB):
    return fdb.select(where=[
        'problem_id=' + prob_id,
        lang_select,
        'during_competition=1'
    ])


def transport_db_to_json():
    udb = UserDB()
    user_dict = generate_dict(udb)
    pdb = ProblemDB()
    fdb = FileDB()
    for prob in pdb.select():
        for sub in get_submissions(prob['problem_id'], fdb):
            pass


if __name__ == '__main__':
    iterator_test()
