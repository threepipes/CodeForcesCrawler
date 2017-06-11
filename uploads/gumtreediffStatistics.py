from Analyzer import Analyzer
from FileChooser import FileChooser

class GtdStatistics(Analyzer):
    def __init__(self, plot_file, file_chooser):
        super().__init__(file_chooser)
        self.plot_file = plot_file
        command = {
            'task': 'diff',
            'method': 'gumtree'
        }
        self.set_command_list(command)

    def write_list(self, file_list):
        pass

    def output(self, file_list, data):
        pass


class DiffFileChooser(FileChooser):
    def get_all_file_list(self):
        pass