from Database import Database

class AcceptanceDB(Database):
    table_name = 'Acceptance'
    key = 'problem_id'
    column = [
        'problem_id',
        'submission_in_sample',
        'solved_in_sample',
        'submission',
        'solved',
        'acceptance_rate',
        'lastmodified'
    ]
    data_table = {
        'problem_id': 'VARCHAR(20)',
        'submission_in_sample': 'INT(6)',
        'solved_in_sample': 'INT(5)',
        'submission': 'INT(6)',
        'solved': 'INT(5)',
        'acceptance_rate': 'DOUBLE',
        'lastmodified': 'DATE'
    }

    def __init__(self):
        super(AcceptanceDB, self).__init__(self.table_name, self.key, self.column, self.data_table)
