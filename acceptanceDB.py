import Database as db

class AcceptanceDB:
    table_name = 'AcceptanceTable'
    key = 'id'
    cols = [
        'id',
        'solved',
        'try_in_sample',
        'solved_in_sample',
        'submission',
        'acceptance_rate',
        'lastmodified'
    ]

    def __init__(self):
        self.con = db.Connector()

    def update(self, prob, keyname):
        self.con.update(prob, self.table_name, {self.key: keyname})

    def getProblems(self, where=None):
        ret = self.con.get(self.table_name, self.cols, where)
        return ret

    def close(self):
        self.con.close()

    def commit(self):
        self.con.commit()
