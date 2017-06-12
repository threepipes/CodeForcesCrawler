from Database import Database
from submissionListGenerator import get_history_list
from userDB import UserDB
from fileDB import FileDB
from Analyzer import CAExecuter


class SubmissionHistory(Database):
    table_name = 'SubmissionDistance'
    key = 'file_name'
    column = [
        'file_name',
        'next_file',
        'levenshtein_distance',
        'add_node',
        'delete_node',
        'update_node'
    ]
    data_table = {
        'file_name': 'VARCHAR(50)',
        'next_file': 'VARCHAR(50)',
        'levenshtein_distance': 'INT(5)',
        'add_node': 'INT(4)',
        'delete_node': 'INT(4)',
        'update_node': 'INT(4)'
    }

    def __init__(self):
        super().__init__(self.table_name, self.key, self.column, self.data_table)


def store_gumtree_result(user_result):
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


def init_db():
    udb = UserDB()
    fdb = FileDB()
    analyzer = CAExecuter()
    for user in udb.select():
        user_name = user['user_name']
        pid_list, hist_list = get_history_list(user_name, fdb, 'src/')
        analyzer.set_command({'task': 'dist', 'method': 'gumtree'})
        analyzer.write_list(hist_list)
        analyzer.execute()
        result = analyzer.read_result()
