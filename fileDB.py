from Database import Connector

class FileDB:
    table_name = 'FileTable'

    def __init__(self):
        self.con = Connector()

    def initTable(self):
        filetable = {
            'file_name': 'VARCHAR(50)',
            'user_name': 'VARCHAR(30)',
            'lang': 'VARCHAR(20)',
            'verdict': 'VARCHAR(20)',
            'timestamp': 'BIGINT UNSIGNED',
            'points': 'INT(5)',
            'prob_index': 'VARCHAR(5)'
        }
        self.con.createTable('FileTable', filetable, primary_key='file_name')

    def close(self):
        self.con.close()

    def addFile(self, username, filename, lang, verdict, timestamp, points):
        data = {
            'file_name': filename,
            'user_name': username,
            'lang': lang,
            'verdict': verdict,
            'timestamp': timestamp,
            'points': points
        }
        if self.con.existKey(self.table_name, 'file_name', filename):
            self.con.update(data, self.table_name, {'file_name': filename})
        else:
            self.con.insert(data, self.table_name)


def updateProbIndex():
    con = Connector()
