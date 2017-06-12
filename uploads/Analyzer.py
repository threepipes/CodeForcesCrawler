from subprocess import Popen, PIPE
import json


def _dict_to_list(_dict):
    return ['%s=%s' % (k, v) for k, v in _dict.items()]


class CAExecuter:
    """
    解析器であるCodeAnalyzerを利用するためのラッパー
    """
    WORKING_DIR = '../data/'
    LIST_FILE = 'file_list.list'
    RESULT_FILE = 'output.data'
    LOG_FILE = 'log.txt'
    LOG_LEVEL = 'all'
    DEFAULT_COMMAND = [
        'java', '-jar', 'analyzer.jar'
    ]
    DEFAULT_OPTION = {
        'task': 'test',
        'inpath': LIST_FILE,
        'outpath': RESULT_FILE,
        'logfile': LOG_FILE,
        'loglevel': LOG_LEVEL
    }

    def __init__(self):
        self.command_list = self.DEFAULT_COMMAND + _dict_to_list(self.DEFAULT_OPTION)

    def set_command(self, command_dict):
        command = self.DEFAULT_OPTION.copy()
        command.update(command_dict)
        self.command_list = self.DEFAULT_COMMAND + _dict_to_list(command)

    def write_list(self, path_list):
        """
        文字列のリストであるpath_listをcsv形式で書き込む
        path_listが1次元の場合は改行区切り
        2次元の場合は，列はカンマ区切り，行は改行区切り
        """
        with open(self.WORKING_DIR + self.LIST_FILE, 'w', encoding='utf-8') as f:
            for row in path_list:
                if isinstance(row, str):
                    f.write(row + '\n')
                else:
                    f.write(','.join(row) + '\n')

    def execute(self):
        p = Popen(self.command_list, cwd=self.WORKING_DIR, stdout=PIPE)
        stdout, stderr = p.communicate()
        print('finish analyze.')
        return stdout

    def read_result(self):
        with open(self.WORKING_DIR + self.RESULT_FILE, encoding='utf-8') as f:
            analyze_result = json.load(f)
        return analyze_result


class Analyzer(CAExecuter):
    def __init__(self, file_chooser):
        super().__init__()
        self.chooser = file_chooser
        self.source_path = 'src/'

    def reset(self, file_chooser):
        self.chooser = file_chooser

    def set_command_list(self, command_dict):
        self.set_command(command_dict)

    def write_list(self, file_list):
        with open(self.WORKING_DIR + self.LIST_FILE, 'w', encoding='utf-8') as f:
            for data in file_list:
                f.write(self.source_path + data['file_name'] + '\n')

    def choose_files(self):
        return self.chooser.get_all_file_list()

    def render(self, file_list, data):
        pass

    def output(self, file_list, data):
        raise NotImplementedError()

    def analyze(self, file_filter=None):
        file_list = self.choose_files()
        if file_filter is not None:
            file_filter.filtering(file_list)
        self.write_list(file_list)
        self.execute()
        analyze_result = self.read_result()
        self.render(file_list, analyze_result)
        self.output(file_list, analyze_result)


class FileFilter:
    def __init__(self):
        pass

    def filtering(self, file_list):
        return filter(self.get_filter(), file_list)

    def get_filter(self):
        return lambda x: True


class AcceptedSubmissionFilter(FileFilter):
    """
    filtering対象
      サンプル内正解提出数が10以上のユーザ提出であること
      正解提出であること
      コンテスト内提出であること
    """
    def __init__(self, user_submission_db):
        super(AcceptedSubmissionFilter, self).__init__()
        user_data = user_submission_db.select()
        table = {}
        for data in user_data:
            table[data['user_name']] = data
        self.table = table

    def get_filter(self):
        def func(file_data):
            user_name = file_data['user_name']
            sub_data = self.table[user_name]
            return sub_data['solved_in_sample'] >= 10 \
               and file_data['verdict'] == 'OK' \
               and file_data['during_competition'] == 1
        return func
