from database.acceptanceDB import AcceptanceDB
from database.problemDB import ProblemDB
from database.userDB import UserDB
from util.data import rating_split

user_div = 'user'
problem_div = 'prob'
tag_div = 'tag'
type_div = 'type'


class DataClassifier:
    name = 'default'

    def __init__(self, clsf_type_name: str):
        self.clsf_type_name = clsf_type_name

    def clsf_type(self):
        return self.clsf_type_name

    def __call__(self, fix_data):
        return 'all'

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
    rating_div = rating_split

    def __init__(self, udb: UserDB):
        super().__init__(user_div)
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

    def __init__(self, adb: AcceptanceDB):
        super().__init__(problem_div)
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

    def __init__(self, pdb: ProblemDB):
        super().__init__(problem_div)
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

    def __init__(self):
        super().__init__(tag_div)

    def __call__(self, fix_data):
        return fix_data['node_type']


class TagParentClassifier(DataClassifier):
    name = 'tagPar'

    def __init__(self):
        super().__init__(tag_div)

    def __call__(self, fix_data):
        return fix_data['parent_type']


class ModificationTypeClassifier(DataClassifier):
    name = 'mod'

    def __init__(self):
        super().__init__(type_div)

    def __call__(self, fix_data):
        return fix_data['modification_type']
