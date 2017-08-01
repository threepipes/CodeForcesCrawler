from userDB import UserDB
from acceptanceDB import AcceptanceDB
from problemDB import ProblemDB

from DistanceAnalyzer import rating_split


user_div = 'user'
problem_div = 'prob'
tag_div = 'tag'
type_div = 'type'


class DataClassifier:
    name = 'default'
    clsf_type_name = 'all'

    def clsf_type(self):
        return self.clsf_type_name

    def __call__(self):
        raise NotImplementedError()

    def __str__(self):
        return self.name


class FixClassifier:
    def __init__(self, classifier_list: list):
        self.classifier_list = classifier_list

    def classifier_name(self, splitter='_'):
        return splitter.join(self.classifier_list)

    def __call__(self, fix_data):
        result = {'data': fix_data}
        for csf in self.classifier_list:
            result[csf.clsf_type()] = csf(fix_data)
        return result, '_'.join(map(str, self.classifier_list))


class UserRatingClassifier(DataClassifier):
    name = 'uRating'
    clsf_type_name = user_div
    rating_div = rating_split

    def __init__(self, udb: UserDB):
        self.user_dict = udb.get_dict()

    def __call__(self, fix_data):
        """
        参加者をレーティングで分類
        """
        user_name = fix_data['user_name']
        user_rating = self.user_dict[user_name]['rating']
        for i, r in enumerate(self.rating_div):
            if user_rating >= r:
                continue
            return str(r)
        return 'none'


class ProbAccClassifier(DataClassifier):
    name = 'probAcc'
    clsf_type_name = problem_div

    def __init__(self, adb: AcceptanceDB):
        self.acc_dict = adb.get_dict()

    def __call__(self, fix_data):
        """
        問題を0.2区切りの正答率で分類
        """
        prob_id = fix_data['problem_id']
        acc = self.acc_dict[prob_id]['acceptance_rate']
        for i in range(5):
            if acc >= (i + 1) * 0.2:
                continue
            return '%.2f' % ((i + 1) * 0.2)
        return '1.00'


class ProbPointClassifier(DataClassifier):
    name = 'probPoint'
    clsf_type_name = problem_div

    def __init__(self, pdb: ProblemDB):
        self.prob_dict = pdb.get_dict()

    def __call__(self, fix_data):
        """
        問題を点数で分類
        500の倍数でない点数は除外
        """
        prob_id = fix_data['problem_id']
        point = self.acc_dict[prob_id]['points']
        if point % 500 != 0:
            return 'other'
        return str(point)


class TagSelfClassifier(DataClassifier):
    name = 'tagSelf'
    clsf_type_name = tag_div

    def __call__(self, fix_data):
        return fix_data['node_type']


class TagParentClassifier(DataClassifier):
    name = 'tagPar'
    clsf_type_name = tag_div

    def __call__(self, fix_data):
        return fix_data['parent_type']


class ModificationTypeClassifier(DataClassifier):
    name = 'mod'
    clsf_type_name = type_div

    def __call__(self, fix_data):
        return fix_data['modification_type']
