import logging
import logger_config


basic_logger = logging.getLogger('basic_logger')
debugger = logging.getLogger('debugger')

class AkariSolver(object):
    def read_board_from_file(self, filename):
        self.current_board = {'board_matrix':None, 'num_cols':None, 'num_rows':None, 'solutions':[]} 
        with open(filename, 'r') as f:
            # Read number of rows and columns:
            for line in f:
                line = line.lower()
                if line[0] == '#': continue 
                num_rows, num_cols = line.split('x')
                self.current_board['num_rows'], self.current_board['num_cols'] = int(num_rows), int(num_cols)
                break
            if self.current_board['num_cols'] is None or self.current_board['num_rows'] is None:
                raise ValueError("Can not read the dimensions of the akari board")
            self.current_board['board_matrix'] = []
            for rowno in range(int(num_rows)):
                line = f.__next__()
                line = line.lower()
                row = line.strip().split()
                #Check integrity of the line:
                for colno, cell in enumerate(row):
                    if cell not in {'w', 'b', 'wl', 'b0', 'b1', 'b2', 'b3', 'b4'}:
                        raise ValueError(f"Invalid {cell = } at line {rowno} and col {colno}")
                self.current_board['board_matrix'].append(row)
            for empty_line in f:
                if len(empty_line.strip()) > 0: 
                    raise ValueError(f"The last lines must be empty. Invalid line: {empty_line.strip()}")

if __name__=='__main__':
    my_client = AkariSolver()
    filename = r'C:\Users\artur\Desktop\semestre\CMC-15_inteligencia_artificial\labs\akari-solver\doc\example_game1.txt'
    my_client.read_board_from_file(filename)
    print(f"{my_client.current_board = }")
