from database.fileDB import FileDB


def list_to_where(col, val_list):
    if isinstance(val_list[0], str):
        vals = map(lambda val: "%s='%s'" % (col, val), val_list)
    else:
        vals = map(lambda val: "%s=%s" % (col, val), str(val_list))
    return '(%s)' % ' or '.join(vals)


class FileChooser:
    LANG = [
        'GNU C++',
        'GNU C++11',
        'GNU C++14',
    ]

    def __init__(self, column):
        self.verdict = [
            'OK',
            'WRONG ANSWER',
            'TIME LIMIT EXCEEDED',
        ]
        self.file_db = FileDB()
        self.column = column
        self.where_lang = list_to_where('lang', self.LANG)
        self.where_verdict = list_to_where('verdict', self.verdict)
        self.key_list = None

    def set_choose_column(self, column_name):
        self.column = column_name

    def set_key_list(self, key_list):
        self.key_list = key_list

    def get_file_list(self, key):
        where = "%s='%s'" % (self.column, key)
        return self.file_db.select(where=[
            where,
            self.where_lang,
            self.where_verdict
        ])

    def generate_file_list(self, mod=100):
        if self.key_list is None:
            print('FileChooser: key must be set')
            return []

        for i, key in enumerate(self.key_list):
            if (i + 1) % mod == 0:
                print('%s/%s' % (i + 1, len(self.key_list)))
            yield self.get_file_list(key)

    def get_all_file_list(self):
        """
        called from Analyzer and returns all file list
        """

        if self.key_list is None:
            print('FileChooser: key must be set')
            return []

        result = []
        for key in self.key_list:
            result += self.get_file_list(key)
        return result


def test_chooser():
    column = 'problem_id'
    key_list = [
        '101A', '101B', '102B', '103C',
    ]
    chooser = FileChooser(column)
    chooser.set_key_list(key_list)
    for file_list in chooser.generate_file_list():
        print(file_list[:5])


if __name__ == '__main__':
    test_chooser()
