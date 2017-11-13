import modification_util.modification_cache_util as mcu
import pandas as pd

block_decl = {
    'if', 'else', 'elseif', 'while', 'function', 'unit', 'for', 'control',
}

uni_decl = {
    'else', 'elseif', 'function', 'unit', 'for'
}

if_decl = {
    'condition', 'then'
}


def processing_block(near_block):
    node, child = near_block
    if node in uni_decl \
            or node == 'while' and child != 'condition' \
            or node == 'if' and child not in if_decl \
            or child == 'comment':
        return node
    return node + ' ' + child


def near_block_each_data():
    """
    block_typeに関するデータリストをユーザーごとに返す
    :return:
    """
    for path, data in mcu.iter_data():
        data_list = []
        for prob, src, src_nx, change_types, i in mcu.iter_src_info(data):
            for change in change_types:
                info_list = change['info']
                first = info_list[0]
                near_block = get_near_block(info_list)
                data_list.append([prob, near_block, first])
        yield path, data_list


def near_block_each_data_sub():
    """
    block_typeに関するデータリストを提出ごとに返す
    :return: src_path, data_list, i(その問題の何番目の提出か)
    """
    for path, data in mcu.iter_data():
        for prob, src, src_nx, change_types, i in mcu.iter_src_info(data):
            data_list = []
            for change in change_types:
                info_list = change['info']
                first = info_list[0]
                near_block = get_near_block(info_list)
                data_list.append([prob, near_block, first])
            yield src, data_list, i


def get_near_block(info_list):
    near_block = None
    """
    親以上のうちblock_declに属する最も近いノードを抜き出す
    """
    for pre, node in zip(info_list, info_list[1:]):
        if node in block_decl:
            near_block = (node, pre)
            break
    near_block = processing_block(near_block)
    return near_block


def trans_blocks2df(data_list):
    columns = ['prob', 'block', 'node']
    df = pd.DataFrame(data_list, columns=columns)
    return df.groupby(columns).size().unstack().fillna(0)


def collect_blockcount():
    multiset = None
    for path, data_list in near_block_each_data():
        df_tmp = trans_blocks2df(data_list)
        if multiset is None:
            multiset = df_tmp
        else:
            multiset.add(df_tmp, fill_value=0)

