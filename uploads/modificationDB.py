from fileDB import FileDB
from userDB import UserDB
from datetime import timedelta
from Database import Database
from contestDB import ContestDB
from Analyzer import CAExecuter

from fileDB_util import filename_to_username, filename_to_submission_id
from submissionListGenerator import get_history_list


class ModificationDB(Database):
    table_name = 'Modification'
    """
    idx: 提出id + 修正における連番id 5桁
    """
    key = 'idx'
    column = [
        'idx',
        'user_name',
        'problem_id',
        'file_name',
        'node_type',
        'parent_type',
        'modification_type',
    ]
    data_table = {
        'idx': 'VARCHAR(20)',
        'user_name': 'VARCHAR(30)',
        'problem_id': 'VARCHAR(6)',
        'file_name': 'VARCHAR(50)',
        'node_type': 'VARCHAR(20)',
        'parent_type': 'VARCHAR(20)',
        'modification_type': 'VARCHAR(4)',
    }

    def __init__(self):
        super().__init__(self.table_name, self.key, self.column, self.data_table)


class GumTreeModification(CAExecuter):
    def __init__(self):
        super().__init__()
        self.set_command({
            'task': 'diff',
            'method': 'gumtreepos',
        })

    def get_gumtree_result(self, user_name: str, fdb: FileDB, save_path=None):
        pid_list, hist_list = get_history_list(user_name, fdb, 'src/')
        try:
            self.write_list(hist_list)
            self.execute()
            result = self.read_result()
            if save_path:
                with open(save_path, 'w') as f:
                    f.write(str((pid_list, hist_list, result)))
        except:
            print('error during analyze: ' + user_name)
            return
        return self.parse_gumtree_result(pid_list, hist_list, result)

    def parse_gumtree_result(self, pid_list, hist_list, result):
        """
        GumTreeDiffの結果をDB格納形式に変換する
        """
        data_list = []
        for i in range(len(hist_list)):
            for j in range(len(hist_list[i]) - 1):
                file_name = hist_list[i][j].split('/')[-1]
                user_name = filename_to_username(file_name)
                submission_id = filename_to_submission_id(file_name)
                index = j + 1
                diff_data_list = result[i][j]
                prob_id = pid_list[i]
                for k, diff_data in enumerate(diff_data_list):
                    node_type = diff_data['info'][0]
                    parent = '-'
                    if len(diff_data['info']) > 1:
                        parent = diff_data['info'][1]
                    data_list.append({
                        'idx': submission_id + ('%02d%05d' % (index, k)),
                        'user_name': user_name,
                        'file_name': file_name,
                        'problem_id': '-',
                        'node_type': node_type,
                        'parent_type': parent,
                        'modification_type': diff_data['type'],
                    })
        return data_list

    def test_analyze(self):
        fdb = FileDB()
        user_name = 'sntea'
        result = self.get_gumtree_result(user_name, fdb)
        for d in result:
            print(d)


def set_problem_id():
    mdb = ModificationDB()
    fdb = FileDB()
    pre_filename = ''
    pre_pid = ''
    udb = UserDB()
    for user in udb.select():
        user_name = user['user_name']
        print(user_name)
        for data in mdb.select(where={'user_name': user_name}):
            file_name = data['file_name']
            if file_name == pre_filename:
                prob_id = pre_pid
            else:
                pre_filename = file_name
                for file_data in fdb.select(where={'file_name': file_name}):
                    prob_id = file_data['problem_id']
                    break
                pre_pid = prob_id
            if prob_id is None:
                prob_id = '-'
            mdb.update(data['idx'], {'problem_id': prob_id})
        mdb.commit()


def create_modification_db():
    mdb = ModificationDB()
    mdb.init_table()
    gtm = GumTreeModification()
    fdb = FileDB()
    udb = UserDB()
    error_list = []
    for i, user in enumerate(udb.select()):
        user_name = user['user_name']
        print('begin [%d] user:%s' % (i, user_name))
        save_path = '../data/modification_cache/%s.log' % user_name
        result_gt = gtm.get_gumtree_result(user_name, fdb, save_path=save_path)
        if not result_gt:
            error_list.append(user_name)
            continue
        print('finish getting result')
        for result in result_gt:
            mdb.insert(result)

        mdb.commit()

    with open('error_log.txt', 'w') as f:
        for err in error_list:
            f.write(err + '\n')


if __name__ == '__main__':
    set_problem_id()
