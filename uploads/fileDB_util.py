lang_list = ['GNU C++14', 'GNU C++11', 'GNU C++']
lang_select = '(%s)' % ' or '.join(["lang='%s'" % lang for lang in lang_list])
base_selection = [
    lang_select,
    # 'during_competition=1',
    "verdict!='COMPILATION_ERROR'"
]
