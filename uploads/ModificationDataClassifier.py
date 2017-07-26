from userDB import UserDB
from acceptanceDB import AcceptanceDB
from problemDB import ProblemDB

from DistanceAnalyzer import rating_split


class FixClassifier:
    t_user = 'user'
    t_prob = 'prob'
    t_tag = 'tag'
    t_type = 'type'

    def __init__(
            self,
            user_clsf=DefaultClassifier(),
            prob_clsf=DefaultClassifier(),
            tag_clsf=DefaultClassifier(),
            type_clsf=DefaultClassifier()
            ):
        self.user_clsf = user_clsf
        self.prob_clsf = prob_clsf
        self.tag_clsf = tag_clsf
        self.type_clsf = type_clsf

    def classifier_name(self, splitter='_'):
        result = splitter.join([
            self.user_clsf.name,
            self.prob_clsf.name,
            self.tag_clsf.name,
            self.type_clsf.name
        ])
        return result

    def classifier(self, fix_data):
        _user = self._user_clsf(fix_data)
        _prob = self._prob_clsf(fix_data)
        _tag = self._tag_clsf(fix_data)
        _type = self._type_clsf(fix_data)
        result = {
            self.t_user: _user,
            self.t_prob: _prob,
            self.t_tag: _tag,
            self.t_type: _type,
            'data': fix_data
        }
        return result, ('%s_%s_%s_%s' % (_user, _prob, _tag, _type))

    def _user_clsf(self, fix_data):
        return self.user_clsf(fix_data)

    def _prob_clsf(self, fix_data):
        return self.prob_clsf(fix_data)

    def _tag_clsf(self, fix_data):
        return self.tag_clsf(fix_data)

    def _type_clsf(self, fix_data):
        return self.type_clsf(fix_data)


class UserRatingClassifier:
    name = 'uRating'
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


class DefaultClassifier:
    name = 'd'

    def __call__(self, fix_data):
        return 'all'


class ProbAccClassifier:
    name = 'probAcc'

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


class ProbPointClassifier:
    name = 'probPoint'

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


class TagSelfClassifier:
    name = 'tagSelf'

    def __call__(self, fix_data):
        return fix_data['node_type']


class TagParentClassifier:
    name = 'tagPar'

    def __call__(self, fix_data):
        return fix_data['parent_type']


class ModificationTypeClassifier:
    name = 'mod'

    def __call__(self, fix_data):
        return fix_data['modification_type']
