import json
import os

from joblib import Parallel, delayed
from database.userSolvedDB import UserSolvedDB

from ModificationDataClassifier import *
from database.fileDB import FileDB
from database.modificationDB import ModificationDB
from plot_util.barhplot import barh_plot_m2


def add_multiset(multiset: dict, data: str, num=1):
    if data is None:
        return
    if data not in multiset:
        multiset[data] = 0
    multiset[data] += num


def add_multiset2(multiset: dict, data1, data2):
    """
    multiset[data1]にdata2を加える
    """
    if data1 not in multiset:
        multiset[data1] = {}
    if data2 not in multiset[data1]:
        multiset[data1][data2] = 0
    multiset[data1][data2] += 1


def add_multiset_deep(ms1: dict, ms2: dict):
    """
    深さ2のmultiset1にmultiset2を加算する
    """
    for tag, ms in ms2.items():
        if tag not in ms1:
            ms1[tag] = {}
        added = ms1[tag]
        for key, value in ms.items():
            if key not in added:
                added[key] = 0
            added[key] += value


def div_multiset(multiset: dict, div: int):
    for tag, ms in multiset.items():
        for key in ms.keys():
            ms[key] /= div


def add_multiset_deep_div(ms1: dict, ms2: dict, div: float):
    """
    深さ2のmultiset1にmultiset2を加算する
    加算の際にdivで割る
    """
    for tag, ms in ms2.items():
        if tag not in ms1:
            ms1[tag] = {}
        added = ms1[tag]
        for key, value in ms.items():
            if key not in added:
                added[key] = 0
            added[key] += value / div


def add_multiset_deep_normalize(ms1: dict, ms2: dict, divisor: dict, div=1):
    for tag, ms in ms2.items():
        if tag not in ms1:
            ms1[tag] = {}
        added = ms1[tag]
        for key, value in ms.items():
            if key not in added:
                added[key] = 0
            added[key] += value * div / divisor[tag][key]


def collect_by_user(
            user_name: str,
            prob_name: str,
            mdb: ModificationDB,
            classifier: FixClassifier,
            divide=True
        ):
    """
    該当ユーザーの該当問題における修正を集計する
    どの位置でどの種類(addなど)の修正が何回起こったかを集計する
    """
    multiset = {}
    where = {
        'user_name': user_name,
        'problem_id': prob_name,
        'during_competition': 1,
    }
    div_name = None
    submit_count = set()
    for fix_data in mdb.select(where=where):
        submit_count.add(fix_data['file_name'])
        data_dict, data_name = classifier(fix_data)
        if div_name is None:
            div_name = data_dict[problem_div] + '_' + data_dict[user_div]
        add_multiset2(
            multiset,
            data_dict[tag_div],
            data_dict[type_div]
        )
    if divide:
        div_multiset(multiset, len(submit_count))
    return multiset, div_name


def collect_by_prob(prob_name: str):
    """
    問題ごとの集計を行う
    問題における中央値や平均の算出も行う
    並列実行のため，独立に実行できるようにしたい
    """
    fdb = FileDB()
    usdb = UserSolvedDB()
    mdb = ModificationDB()
    adb = AcceptanceDB()
    udb = UserDB()
    classifier = build_mod_classifier_ex(adb, udb)
    where = {'problem_id': prob_name}
    ms_fixdata = {}
    user_count = {}
    for user in usdb.select(col=['user_name'], where=where):
        user_name = user['user_name']
        ms, name = collect_by_user(
            user_name, prob_name,
            mdb, classifier, False
        )
        add_multiset(user_count, name)
        if name not in ms_fixdata:
            ms_fixdata[name] = {}
        add_multiset_deep(ms_fixdata[name], ms)

    return ms_fixdata, user_count


def collect_by_prob_normalized(prob_name: str):
    """
    問題ごとの集計を行う
    問題における中央値や平均の算出も行う
    並列実行のため，独立に実行できるようにしたい
    """
    # fdb = FileDB()
    usdb = UserSolvedDB()
    mdb = ModificationDB()
    adb = AcceptanceDB()
    udb = UserDB()
    classifier = build_userless_classifier(adb)
    where = {'problem_id': prob_name}
    user_list = usdb.select(col=['user_name'], where=where)
    fixdata_alluser = {}
    user_count = 0
    for user in user_list:
        user_count += 1
        user_name = user['user_name']
        ms, name = collect_by_user(
            user_name, prob_name,
            mdb, classifier
        )
        add_multiset_deep(fixdata_alluser, ms)

    classifier = build_mod_classifier_ex(adb, udb)
    ms_fixdata = {}
    for user in user_list:
        user_name = user['user_name']
        ms, name = collect_by_user(
            user_name, prob_name,
            mdb, classifier
        )
        # normalize
        if name not in ms_fixdata:
            ms_fixdata[name] = {}
        add_multiset_deep_normalize(
            ms_fixdata[name], ms, fixdata_alluser, user_count
        )

    return ms_fixdata, user_count


def parallel_collect(divide=True):
    pdb = ProblemDB()
    prob_list = [prob['problem_id'] for prob in pdb.select()]
    fixdata_list = Parallel(n_jobs=6, verbose=10)(
        delayed(collect_by_prob)(p) for p in prob_list
    )
    # fixdata_list = []
    # for prob_id in prob_list[1000:1002]:
    #     fixdata_list.append(collect_by_prob(prob_id))

    ms_fixdata = {}
    div_name_count = {}
    for fixdata_part, user_count in fixdata_list:
        for div_name, fixdata in fixdata_part.items():
            if div_name is None:
                continue
            if div_name not in ms_fixdata:
                ms_fixdata[div_name] = {}
            if divide:
                add_multiset_deep_div(
                    ms_fixdata[div_name],
                    fixdata, user_count[div_name]
                )
            else:
                add_multiset_deep(
                    ms_fixdata[div_name],
                    fixdata)
            add_multiset(div_name_count, div_name)

    if divide:
        for div_name, ms in ms_fixdata.items():
            div_multiset(ms, div_name_count[div_name])

    return ms_fixdata


def get_type_order():
    order = [
        {'name': 'INS', 'color': (1, 0, 0)},
        {'name': 'DEL', 'color': (0, 1, 1)},
        {'name': 'UPD', 'color': (0, 1, 0)},
        {'name': 'MOV', 'color': (0, 0, 1)},
    ]
    return order


def build_userless_classifier(adb: AcceptanceDB):
    clsf_prob = ProbAccClassifier(adb)
    clsf_user = DataClassifier(user_div)
    clsf_tag = TagParentClassifier()
    clsf_type = ModificationTypeClassifier()
    classifier = FixClassifier([
        clsf_prob, clsf_user, clsf_tag, clsf_type
    ])
    return classifier


def build_mod_classifier_ex(adb: AcceptanceDB, udb: UserDB):
    clsf_prob = ProbAccClassifier(adb)
    clsf_user = UserRatingClassifier(udb)
    clsf_tag = TagParentClassifier()
    clsf_type = ModificationTypeClassifier()
    classifier = FixClassifier([
        clsf_prob, clsf_user, clsf_tag, clsf_type
    ])
    return classifier


collect_data_dir = 'stat_fix_data_s_par_dc/'
collect_data_path = collect_data_dir + '%s.json'


def save_collect_data(name, data_dict):
    with open(collect_data_path % name, 'w') as f:
        json.dump(data_dict, f)


def load_collect_data(name):
    with open(collect_data_path % name) as f:
        return json.load(f)


def collect_plot_prob_fix():
    data = parallel_collect(False)

    mdb = ModificationDB()
    tag_list = [fix['parent_type'] for fix in mdb.select(
        col=['parent_type'], distinct=True
    )]

    for name, data_dict in data.items():
        if not os.path.exists(collect_data_dir):
            os.mkdir(collect_data_dir)
        save_collect_data(name, data_dict)

    save_dir = collect_data_dir  # 'plot_fix_data_norm_s_par_dc/'
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    for name, data_dict in data.items():
        print(name)
        barh_plot_m2(
            data_dict, get_type_order(), tag_list, xlim=(0, 200),
            title=name, path=(save_dir + '%s.png' % name)
        )


def sort_tags(tag_list, data_dict, n=-1):
    data_list = []
    for key in tag_list:
        ms = data_dict.get(key, {})
        sum_value = 0
        for v in ms.values():
            sum_value += v
        data_list.append((sum_value, key))
    result = [v[1] for v in sorted(data_list, key=lambda v: v[0])]
    if n > 0:
        return result[-n:]
    else:
        return result


output_list = {
    '0.40_1200', '0.40_1900'
}


def collect_plot_from_file():
    # mdb = ModificationDB()
    # tag_list = [fix['parent_type'] for fix in mdb.select(
    #     col=['parent_type'], distinct=True
    # )]
    # with open('par_tag_list.json', 'w') as f:
    #     json.dump(tag_list, f)
    with open('par_tag_list.json') as f:
        tag_list = json.load(f)
    save_dir = 'plot_fix_data_par_log/'
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    for file_name in os.listdir(collect_data_dir):
        name, ext = os.path.splitext(file_name)
        if ext != '.json':
            continue
        if name not in output_list:
            continue
        print(name)
        data_dict = load_collect_data(name)
        # barh_plot_m2(
        #     data_dict, get_type_order(), tag_list, xlim=(0, 70),
        #     title=name, path=(save_dir + '%s.png' % name)
        # )
        barh_plot_m2(
            data_dict, get_type_order(), sort_tags(tag_list, data_dict, n=10), xlim=None,
            title=None, path=(save_dir + '%s.eps' % name), figsize=(8, 6)
        )


if __name__ == '__main__':
    collect_plot_from_file()
