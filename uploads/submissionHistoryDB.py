from Database import Database
from submissionListGenerator import get_history_list
from userDB import UserDB
from fileDB import FileDB
from Analyzer import CAExecuter


class SubmissionHistoryDB(Database):
    table_name = 'SubmissionDistance'
    key = 'file_name'
    column = [
        'file_name',
        'next_file',
        # (user, problem)に対する何番目の提出か
        'submission_index',
        'levenshtein_distance',
        'add_node',
        'delete_node',
        'update_node'
    ]
    data_table = {
        'file_name': 'VARCHAR(50)',
        'next_file': 'VARCHAR(50)',
        'submission_index': 'INT(3)',
        'levenshtein_distance': 'INT(5)',
        'add_node': 'INT(4)',
        'delete_node': 'INT(4)',
        'update_node': 'INT(4)'
    }

    def __init__(self):
        super().__init__(self.table_name, self.key, self.column, self.data_table)


def parse_gumtree_result(user_result):
    """
    CodeAnalyzerのgumtreediffによる結果をパースする
    各提出について，(add, delete, update)のタプルに変換した結果を返す
    """
    table = {'insert': 0, 'delete': 1, 'update': 2}
    result = []
    for row in user_result:
        row_result = []
        for col in row:
            act_count = (0, 0, 0)
            for act in col['actions']:
                act_count[table[act['action']]] += 1
            row_result.append(act_count)
        result.append(row_result)
    return result


def store_user_result(hist_list, result_gt, result_lv, sdb):
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
            else:
                next_file = '-'
                leven_dist = 0
                add = 0
                delete = 0
                update = 0
            submission_index = j + 1
            sdb.insert({
                'file_name': file_name,
                'next_file': next_file,
                'submission_index': submission_index,
                'levenshtein_distance': leven_dist,
                'add_node': add,
                'delete_node': delete,
                'update_node': update
            })
    sdb.commit()


def store_user_statistics( \
        user_name: str, \
        fdb: FileDB, \
        analyzer: CAExecuter, \
        sdb: SubmissionHistoryDB):
    """
    あるuserの提出履歴に対する差分配列を取得し，
    DBに格納する．
    """
    pid_list, hist_list = get_history_list(user_name, fdb, 'src/')
    analyzer.set_command({'task': 'dist', 'method': 'gumtree'})
    analyzer.write_list(hist_list)
    analyzer.execute()
    result_gt = analyzer.read_result()
    result_gt = parse_gumtree_result(result_gt)
    analyzer.set_command({'task': 'dist', 'method': 'leven'})
    analyzer.execute()
    result_lv = analyzer.read_result()
    store_user_result(hist_list, result_gt, result_lv, sdb)


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
    for user in udb.select():
        store_user_statistics(user['user_name'], fdb, analyzer, sdb)
