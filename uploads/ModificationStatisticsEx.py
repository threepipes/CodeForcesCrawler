from joblib import Parallel, delayed

from submissionHistoryDB import SubmissionHistoryDB
from fileDB import FileDB
from problemDB import ProblemDB
from userDB import UserDB
from modificationDB import ModificationDB

from ModificationDataClassifier import *
from barhplot import barh_plot_m2


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


def collect_by_user(
            user_name: str,
            prob_name: str,
            mdb: ModificationDB,
            classifier: FixClassifier,
            multiset: dict
        ):
    """
    該当ユーザーの該当問題における修正を集計する
    どの位置でどの種類(addなど)の修正が何回起こったかを集計する
    """
    where = {'user_name': user_name, 'problem_id': prob_name}
    div_name = None
    for fix_data in mdb.select(where=where):
        data_dict, data_name = classifier(fix_data)
        if div_name is None:
            div_name = data_dict[problem_div] + '_' + data_dict[user_div]
            if div_name not in multiset:
                multiset[div_name] = {}
        add_multiset2(
            multiset[div_name],
            data_dict[tag_div],
            data_dict[type_div]
        )
    return div_name


def collect_by_prob(prob_name: str):
    """
    問題ごとの集計を行う
    問題における中央値や平均の算出も行う
    並列実行のため，独立に実行できるようにしたい
    """
    fdb = FileDB()
    mdb = ModificationDB()
    adb = AcceptanceDB()
    udb = UserDB()
    classifier = build_mod_classifier_ex(adb, udb)
    where = {'problem_id': prob_name}
    ms_fixdata = {}
    user_count = 0
    for user in fdb.select(col=['user_name'], distinct=True, where=where):
        user_count += 1
        user_name = user['user_name']
        collect_by_user(
            user_name, prob_name,
            mdb, classifier, ms_fixdata
        )

    return ms_fixdata, user_count


def parallel_collect():
    pdb = ProblemDB()
    prob_list = [prob['problem_id'] for prob in pdb.select()]
    fixdata_list = Parallel(n_jobs=6, verbose=10)(
        delayed(collect_by_prob)(p) for p in prob_list
    )

    ms_fixdata = {}
    for fixdata_part, user_count in fixdata_list:
        for div_name, fixdata in fixdata_part.items():
            if div_name not in ms_fixdata:
                ms_fixdata[div_name] = {}
            add_multiset_deep_div(ms_fixdata[div_name], fixdata)

    return ms_fixdata


def get_type_order():
    order = [
        {'name': 'INS', 'color': (1, 0, 0)},
        {'name': 'DEL', 'color': (0, 1, 1)},
        {'name': 'UPD', 'color': (0, 1, 0)},
        {'name': 'MOV', 'color': (0, 0, 1)},
    ]
    return order


def build_mod_classifier_ex(adb: AcceptanceDB, udb: UserDB):
    clsf_prob = ProbAccClassifier(adb)
    clsf_user = UserRatingClassifier(udb)
    clsf_tag = TagParentClassifier()
    clsf_type = ModificationTypeClassifier()
    classifier = FixClassifier([
        clsf_prob, clsf_user, clsf_tag, clsf_type
    ])
    return classifier


def collect_plot_prob_fix():
    data = parallel_collect()

    for name, data_dict in data.items():
        print(name)
        barh_plot_m2(
            data_dict, get_type_order(),
            title=name, path=('plot_fix_data/%s.png' % name)
        )

if __name__ == '__main__':
    collect_plot_prob_fix()
