from fileDB import FileDB

lang_list = ['GNU C++14', 'GNU C++11', 'GNU C++']
lang_select = '(%s)' % ' or '.join(["lang='%s'" % lang for lang in lang_list])
base_selection = [
    lang_select,
    # 'during_competition=1',
    "verdict!='COMPILATION_ERROR'"
]


def get_file(file_name: str, fdb: FileDB):
    file_data = list(fdb.select(where={'file_name': file_name}))
    if len(file_data) == 0:
        return None
    return file_data[0]
