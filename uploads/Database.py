from Connector import Connector

class Database:
    foreign_key = None
    def __init__(self, table_name, key, column, data_table):
        self.table_name = table_name
        self.key = key
        self.column = column
        self.data_table = data_table
        self.con = Connector()

    def init_table(self, drop=False):
        self.con.createTable(
            self.table_name,
            self.data_table,
            primary_key=self.key,
            foreign_key=self.foreign_key,
            drop=drop
        )

    def close(self):
        self.con.close()

    def insert(self, insert_data):
        if not self.key in insert_data:
            print('Error: no primary key in insert_data')
            return
        data = {}
        for col in self.column:
            if col in insert_data:
                data[col] = insert_data[col]
        if self.con.existKey(self.table_name, self.key, insert_data[self.key]):
            self.con.update(data, self.table_name, {self.key: insert_data[self.key]})
        else:
            self.con.insert(data, self.table_name)

    def update(self, keyname, update_data):
        self.con.update(update_data, self.table_name, {self.key: keyname})

    def select(self, col=None, where=None, limit=-1):
        if col is None:
            col = self.column
        return self.con.get(self.table_name, col, where, limit)

    def count(self):
        return self.con.count(self.table_name)

    def commit(self):
        self.con.commit()

    def drop(self):
        self.con.dropTable(self.table_name)
