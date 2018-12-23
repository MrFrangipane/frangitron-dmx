

class Streamer(object):

    def __init__(self):
        self.programs = list()
        self.selected_program = -1

    def load(self):
        self.programs = ['Blackout', 'ChitChat', 'Lounge', 'Club', 'Searchlight', 'Apocalypse']

    def program_clicked(self, program_name):
        self.selected_program = self.programs.index(program_name)

    def ui_status(self):
        return {
            'selected_program': self.programs[self.selected_program]
        }
