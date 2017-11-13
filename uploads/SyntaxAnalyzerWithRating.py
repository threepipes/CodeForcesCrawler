from SyntaxAnalyzer import SyntaxAnalyzer, colors
from database.userDB import UserDB

class SyntaxAnalyzerWithRating(SyntaxAnalyzer):
    def __init__(self, plot_file, file_chooser, command_dict):
        super(SyntaxAnalyzerWithRating, self) \
            .__init__(plot_file, file_chooser, command_dict)

    def label_mapping(self):
        self.map_key = 'user_name'
        label_table = {}
        udb = UserDB()
        for user in udb.select():
            label_table[user[self.map_key]] = user['rating']
        self.label_table = label_table

    def to_label(self, file_data):
        return str(self.label_table[file_data[self.map_key]])

    def to_color(self, file_data):
        val = min(1, self.label_table[file_data[self.map_key]] / 2500)
        for col in colors:
            if val < col[1]:
                return col[0]
        return (0, 0, 0)
