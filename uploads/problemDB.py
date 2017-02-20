from Database import Database

class ProblemDB(Database):
    table_name = 'Problem'
    key = 'problem_id'
    column = [
        'problem_id',
        'prob_index',
        'competition_id',
        'points'
    ]
    data_table = {
        'problem_id': 'VARCHAR(20)',
        'prob_index': 'VARCHAR(5)',
        'competition_id': 'INT(10)',
        'points': 'INT(5)'
    }

    def __init__(self):
        super(ProblemDB, self).__init__(self.table_name, self.key, self.column, self.data_table)
