from Database import Database
from submissionListGenerator import get_history_list
from userDB import UserDB
from fileDB import FileDB
from Analyzer import CAExecuter

from fileDB_util import base_selection


class SubmissionHistoryDB(Database):
    table_name = 'SubmissionDistance'
    key = 'file_name'
    column = [
        'file_name',
        'next_file',
        'problem_id',
        # (user, problem)に対する何番目の提出か
        'submission_index',
        'levenshtein_distance',
        'add_node',
        'delete_node',
        'update_node',
        'move_node',
        'node_sum',
    ]
    data_table = {
        'file_name': 'VARCHAR(50)',
        'next_file': 'VARCHAR(50)',
        'problem_id': 'VARCHAR(6)',
        'submission_index': 'INT(3)',
        'levenshtein_distance': 'INT(5)',
        'add_node': 'INT(4)',
        'delete_node': 'INT(4)',
        'update_node': 'INT(4)',
        'move_node': 'INT(4)',
        'node_sum': 'INT(5)'
    }

    def __init__(self):
        super().__init__(self.table_name, self.key, self.column, self.data_table)


def parse_gumtree_result(user_result):
    """
    CodeAnalyzerのgumtreediffによる結果をパースする
    各提出について，(add, delete, update)のタプルに変換した結果を返す
    """
    table = {'insert': 0, 'delete': 1, 'update': 2, 'move': 3}
    result = []
    for row in user_result:
        row_result = []
        for col in row:
            act_count = [0, 0, 0, 0]
            for act in col['actions']:
                act_count[table[act['action']]] += 1
            row_result.append(act_count)
        result.append(row_result)
    return result


def store_user_result(hist_list, result_gt, result_lv, sdb, pid_list):
    """
    取得した差分配列をDBに格納
    hist_list: 提出履歴のリスト
    result_gt: hist_listに対するgumtreeによる差分
    result_lv: hist_listに対するlevenshteinによる差分
    全部同じ形(ただしhist_listよりresultは1列少ない)を前提
    """
    for i in range(len(hist_list)):
        for j in range(len(hist_list[i])):
            file_name = hist_list[i][j].split('/')[-1]
            if j < len(hist_list[i]) - 1:
                next_file = hist_list[i][j + 1].split('/')[-1]
                leven_dist = result_lv[i][j]
                gumtree_data = result_gt[i][j]
                add = gumtree_data[0]
                delete = gumtree_data[1]
                update = gumtree_data[2]
                move = gumtree_data[3]
            else:
                next_file = '-'
                leven_dist = 0
                add = 0
                delete = 0
                update = 0
                move = 0
            submission_index = j + 1
            sdb.insert({
                'file_name': file_name,
                'next_file': next_file,
                'problem_id': pid_list[i],
                'submission_index': submission_index,
                'levenshtein_distance': leven_dist,
                'add_node': add,
                'delete_node': delete,
                'update_node': update,
                'move_node': move,
                'node_sum': add + delete + update + move,
            })
    sdb.commit()


def store_user_statistics(
        user_name: str,
        fdb: FileDB,
        analyzer: CAExecuter,
        sdb: SubmissionHistoryDB):
    """
    あるuserの提出履歴に対する差分配列を取得し，
    DBに格納する．
    """
    if exist_user(user_name, fdb, sdb):
        return
    pid_list, hist_list = get_history_list(user_name, fdb, 'src/')
    try:
        analyzer.set_command({'task': 'diff', 'method': 'gumtree'})
        analyzer.write_list(hist_list)
        analyzer.execute()
        result_gt = analyzer.read_result()
        result_gt = parse_gumtree_result(result_gt)
        analyzer.set_command({'task': 'diff', 'method': 'leven'})
        analyzer.execute()
        result_lv = analyzer.read_result()
    except:
        print('error during analyze: ' + user_name)
        return
    store_user_result(hist_list, result_gt, result_lv, sdb, pid_list)


def exist_user(user_name, fdb, sdb):
    where_file = ["user_name='%s'" % user_name] + base_selection
    repr_files = list(fdb.select(where=where_file, limit=1))
    if len(repr_files) == 0:
        return True
    repr_file = repr_files[0]['file_name']
    return len(list(sdb.select(where={'file_name': repr_file}))) > 0


def set_problem_id():
    fdb = FileDB()
    sdb = SubmissionHistoryDB()
    for i, sub_data in enumerate(sdb.select()):
        if (i + 1) % 1000 == 0:
            print(i + 1)
            sdb.commit()
        if not sub_data['problem_id'] is None:
            continue
        name = sub_data['file_name']
        file_data = list(fdb.select(where={'file_name': name}))
        if len(file_data) == 0:
            continue
        file_data = file_data[0]
        if file_data['problem_id'] is None:
            file_data['problem_id'] = '-'
        sdb.update(name, {'problem_id': file_data['problem_id']})
    sdb.commit()


def init_db():
    """
    UserDB, FileDB, sourceから
    SubmissionHistoryDBを構成する
    """
    udb = UserDB()
    fdb = FileDB()
    sdb = SubmissionHistoryDB()
    sdb.init_table()
    analyzer = CAExecuter()
    for i, user in enumerate(udb.select()):
        print(user['user_name'], i)
        store_user_statistics(user['user_name'], fdb, analyzer, sdb)


if __name__ == '__main__':
    set_problem_id()
