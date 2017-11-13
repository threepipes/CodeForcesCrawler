from database.fileDB import FileDB

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


def filename_to_username(file_name: str):
    spl = file_name.split('_')
    suffix_len = len(spl[-1]) + 1 + len(spl[-2]) + 1
    return file_name[:-suffix_len]


def filename_to_submission_id(file_name: str):
    return file_name.split('_')[-2]


def test_f2u():
    file_name = 'te_st_111111_222.src'
    print(filename_to_username(file_name))

if __name__ == '__main__':
    test_f2u()
