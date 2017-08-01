from submissionHistoryDB import SubmissionHistoryDB
from fileDB import FileDB
from problemDB import ProblemDB
from userDB import UserDB
from modificationDB import ModificationDB

from ModificationDataClassifier import *
from barhplot import barh_plot_m2


def add_multiset2(multiset: dict, data1, data2):
    if data1 not in multiset:
        multiset[data1] = {}
    if data2 not in multiset[data1]:
        multiset[data1][data2] = 0
    multiset[data1][data2] += 1


class DataCollector:
    def __init__(
                self,
                sdb: SubmissionHistoryDB,
                fdb: FileDB,
                pdb: ProblemDB,
                udb: UserDB,
                mdb: ModificationDB,
                classifier: FixClassifier
            ):
        self.sdb = sdb
        self.fdb = fdb
        self.pdb = pdb
        self.mdb = mdb
        self.classifier = classifier
        self.user_list = list(udb.select())

    def collect_by_user(self, user_name, prob_name, multiset3=None):
        """
        該当ユーザーの該当問題における修正を集計する
        どの位置でどの種類(addなど)の修正が何回起こったかを集計する
        """
        where = {'user_name': user_name, 'problem_id': prob_name}
        div_name = None
        multiset = {}
        for fix_data in self.mdb.select(where=where):
            data_dict, data_name = self.classifier(fix_data)
            if div_name is None:
                div_name = data_dict[problem_div] + '_' + data_dict[user_div]
                if multiset3:
                    if div_name not in multiset3:
                        multiset3[div_name] = {}
                    multiset = multiset3[div_name]
            add_multiset2(multiset, data_dict[tag_div], data_dict[type_div])
        return multiset, div_name

    def collect_by_prob(self, prob_name, multiset3):
        """
        問題ごとの集計を行う
        問題における中央値や平均の算出も行う
        """
        for user in self.user_list:
            user_name = user['user_name']
            _, div_name = self.collect_by_user(user_name, prob_name, multiset3)

    def collect(self):
        database = {}
        for prob in self.pdb.select():
            prob_id = prob['problem_id']
            self.collect_by_prob(prob_id, database)


def get_type_order():
    order = [
        {'name': 'INS', 'color': (1, 0, 0)},
        {'name': 'DEL', 'color': (0, 1, 1)},
        {'name': 'UPD', 'color': (0, 1, 0)},
        {'name': 'MOV', 'color': (0, 0, 1)},
    ]
    return order


def test_collect_by_user():
    adb = AcceptanceDB()
    udb = UserDB()
    collector = DataCollector(
        SubmissionHistoryDB(),
        FileDB(),
        ProblemDB(),
        UserDB(),
        ModificationDB(),
        build_mod_classifier_ex(adb, udb)
    )
    collect_data, div_name = collector.collect_by_user('-77-', '707B')

    print(div_name)
    print(collect_data)

    barh_plot_m2(collect_data, get_type_order(), div_name)


def build_mod_classifier_ex(adb: AcceptanceDB, udb: UserDB):
    clsf_prob = ProbAccClassifier(adb)
    clsf_user = UserRatingClassifier(udb)
    clsf_tag = TagParentClassifier()
    clsf_type = ModificationTypeClassifier()
    classifier = FixClassifier([
        clsf_prob, clsf_user, clsf_tag, clsf_type
    ])
    return classifier


def plot_mod_h_ex():
    pass


if __name__ == '__main__':
    test_collect_by_user()
