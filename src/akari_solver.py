import logging
import logger_config


basic_logger = logging.getLogger('basic_logger')
debugger = logging.getLogger('debugger')

class AkariSolver(object):
    def __init__(self):
        self.current_board = None

    def read_board_from_file(self, filename):
        self.current_board = {'board_matrix':None, 'num_cols':None, 'num_rows':None, 'solutions':[]} 
        basic_logger.info(f'Reading board from:{filename}')
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
        basic_logger.info('Board successfully read')
        board_content = []
        for line in self.current_board['board_matrix']:
            board_content.append(str(line))
        board_str = '\n'.join(board_content)
        basic_logger.info(f'Board content: \n{board_str}')

    def solve(self):
        if self.current_board is None:
            # No board assigned
            return None

        if len(self.current_board['solutions']) == 0:
            #Solve the problem:
            variables = set()
            tmp_variables_list = []
            for i, row in enumerate(self.current_board['board_matrix']):
                tmp_var_row = []
                for j, cell in enumerate(row):
                    if cell == 'w':
                        domain = {0, 1}
                    elif cell == 'wl':
                        domain = {1}
                    elif cell[0] == 'b':
                        # It is not necessary to store B. It will be useful only for building constraints.
                        if cell == 'b':
                            value = None
                        else:
                            value = int(cell[1:])
                        tmp_var_row.append(('b', value))
                        continue
                    new_variable = Variable(f'A{i},{j}', domain)
                    variables.add(new_variable)
                    tmp_var_row.append(new_variable)
                tmp_variables_list.append(tmp_var_row)
            # Create constraints:
            constraints = dict()
            for i, row in enumerate(tmp_variables_list):
                tmp_row = []
                for j, cell in enumerate(row):
                    if isinstance(cell, tuple):
                        if cell[1] is not None:
                            if cell[1] == 0:
                                b_constraint = [[], lambda *args: sum(args) == 0, "b_constraint (expects 0)"]
                            elif cell[1] == 1:
                                b_constraint = [[], lambda *args: sum(args) == 1, "b_constraint(expects 1)"]
                            elif cell[1] == 2:
                                b_constraint = [[], lambda *args: sum(args) == 2, "b_constraint(expects 2)"]
                            elif cell[1] == 3:
                                b_constraint = [[], lambda *args: sum(args) == 3, "b_constraint(expects 3)"]
                            elif cell[1] == 4:
                                b_constraint = [[], lambda *args: sum(args) == 4, "b_constraint(expects 4)"]
                            #Get b constraint:
                            if j - 1 >= 0:
                                left = tmp_variables_list[i][j - 1]
                                if not isinstance(left, tuple):
                                    b_constraint[0].append(left)
                                    tmp = constraints.get(left, [])
                                    tmp.append(b_constraint)
                                    constraints[left] = tmp
                            if i - 1 >= 0:
                                upper = tmp_variables_list[i - 1][j]
                                if not isinstance(upper, tuple):
                                    b_constraint[0].append(upper)
                                    tmp = constraints.get(upper, [])
                                    tmp.append(b_constraint)
                                    constraints[upper] = tmp
                            if j + 1 < len(tmp_variables_list[i]):
                                right = tmp_variables_list[i][j + 1]
                                if not isinstance(right, tuple):
                                    b_constraint[0].append(right)
                                    tmp = constraints.get(right, [])
                                    tmp.append(b_constraint)
                                    constraints[right] = tmp
                            if i + 1 < len(tmp_variables_list):
                                down = tmp_variables_list[i + 1][j]
                                if not isinstance(down, tuple):
                                    b_constraint[0].append(down)
                                    tmp = constraints.get(down, [])
                                    tmp.append(b_constraint)
                                    constraints[down] = tmp
                            b_constraint[0] = tuple(b_constraint[0])

                        if len(tmp_row) > 0:
                            # Get new row constraint:
                            row_constraint = [[], lambda *args: sum(args) <= 1 and sum(args) >= 0, "row_constraint"]
                            for variable in tmp_row:
                                row_constraint[0].append(variable)
                                tmp = constraints.get(variable, [])
                                tmp.append(row_constraint)
                                constraints[variable] = tmp
                            tmp_row = []
                    else:
                        tmp_row.append(cell)
                if len(tmp_row) > 0:
                    # Get new row constraint:
                    row_constraint = [[], lambda *args: sum(args) <= 1 and sum(args) >= 0, "row_constraint"]
                    for variable in tmp_row:
                        row_constraint[0].append(variable)
                        tmp = constraints.get(variable, [])
                        tmp.append(row_constraint)
                        constraints[variable] = tmp
                    tmp_row = []
            # Get column constraints:
            for j, _ in enumerate(tmp_variables_list[0]):
                tmp_col = []
                for i, _ in enumerate(tmp_variables_list):
                    cell = tmp_variables_list[i][j]
                    if isinstance(cell, tuple):
                        if len(tmp_col) > 0:
                            # Get new row constraint:
                            col_constraint = [[], lambda *args: sum(args) <= 1 and sum(args) >= 0, "col_constraint"]
                            for variable in tmp_col:
                                col_constraint[0].append(variable)
                                tmp = constraints.get(variable, [])
                                tmp.append(col_constraint)
                                constraints[variable] = tmp
                            tmp_col = []
                    else:
                        tmp_col.append(cell)
                if len(tmp_col) > 0:
                    # Get new col constraint:
                    col_constraint = [[], lambda *args: sum(args) <= 1 and sum(args) >= 0, "col_constraint"]
                    for variable in tmp_col:
                        col_constraint[0].append(variable)
                        tmp = constraints.get(variable, [])
                        tmp.append(col_constraint)
                        constraints[variable] = tmp
                    tmp_col = []

            # Get column_row constraints:
            for i, _ in enumerate(tmp_variables_list):
                for j, _ in enumerate(tmp_variables_list[0]):
                    variable = tmp_variables_list[i][j]
                    if isinstance(variable, tuple): # It is not a White cell
                        continue
                    col_row_constraint = [[], lambda *args: (sum(args) <= 2) and (sum(args) > 0), "col_row_constraint"]
                    col_row_constraint[0].append(variable)
                    col_row_constraint[0].extend(get_line_and_column_elements(i, j, tmp_variables_list, stop_func=lambda element: isinstance(element, tuple) and element[0]=='b'))
                    tmp = constraints.get(variable, [])
                    tmp.append(col_row_constraint)
                    constraints[variable] = tmp

            solver = ConstraintSatisfactionProblem(variables, constraints)
            self.current_board['solutions'].append(solver.backtracking_search())
        return self.current_board['solutions']

def get_line_and_column_elements(rowno, colno, matrix, col=True, row=True, stop_func=lambda element:False):
    result = []
    if col:
        # Go up:
        i = rowno - 1
        while i >= 0 and not stop_func(matrix[i][colno]):
            current_element = matrix[i][colno]
            result.append(current_element)
            i -= 1
        # Go down:
        i = rowno + 1
        while i < len(matrix) and not stop_func(matrix[i][colno]):
            current_element = matrix[i][colno]
            result.append(current_element)
            i += 1

    if row:
        # Go right:
        j = colno + 1
        while j < len(matrix[0]) and not stop_func(matrix[rowno][j]):
            current_element = matrix[rowno][j]
            result.append(current_element)
            j += 1
        # Go left:
        j = colno - 1
        while j >= 0 and not stop_func(matrix[rowno][j]):
            current_element = matrix[rowno][j]
            result.append(current_element)
            j -= 1
    return result




class ConstraintSatisfactionProblem(object):
    def __init__(self, variables, constraints):
        if not isinstance(variables, set):
            raise TypeError("variables must be a set")
        self.variables = variables
        self.constraints = constraints

    def backtracking_search(self):
        return self._backtrack(dict())

    def _backtrack(self, assignment:dict):
        if len(assignment) == len(self.variables):
            # Check if the assignment is valid:
            if self._is_valid(assignment):
                return assignment
            else:
                return None
        var = self._select_unassigned_variable(assignment)
        # Naive domain values loop:
        for value in var.domain:
            assignment[var] = value
            if self._is_consistent_value(var, assignment):
                result = self._backtrack(assignment)
                if result is not None:
                    return result
            del assignment[var]
        return None

    def _is_consistent_value(self, var, assignment):
        #check if the constraints will be satisfied:
        for constraint in self.constraints[var]:
            tuple_space = []
            for arg in constraint[0]:
                if arg not in assignment:
                    element = arg.domain
                else:
                    element = {assignment[arg]}
                tuple_space.append(element)
            final_tuples = get_tuples_from_tuple_space(tuple_space)
            result = False
            for assignment_tuple in final_tuples:
                if constraint[1](*assignment_tuple):
                    result = True
                    break
            if not result:
                break
        return result 

    def _is_valid(self, assignment):
        for variable in self.variables:
            if not self._is_consistent_value(variable, assignment):
                return False
        return True

    def _inference(self, var, assignment):
        pass

    def _select_unassigned_variable(self, assignment):
        # Naive implementation
        for variable in self.variables:
            if variable not in assignment:
                return variable


class Variable(object):
    def __init__(self, name, domain):
        if not isinstance(name, str):
            raise TypeError("name must be a str")
        if not isinstance(domain, set):
            raise TypeError("domain must be a set")
        self.name = name
        self.domain = domain
        self.value = None

    def __repr__(self):
        return f'{self.name}'

    def is_in_domain(self, value):
        return value in domain

def get_tuples_from_tuple_space(tuple_space):
    previous_result = [[]]
    current_result  = []
    for el_set in tuple_space:
        for el in el_set:
            for lst in previous_result:
                tmp = lst.copy()
                tmp.append(el)
                current_result.append(tmp)
        #Update results:
        previous_result = current_result
        current_result = []
    for lst in previous_result:
        current_result.append(tuple(lst))
    return tuple(current_result)
        




if __name__=='__main__':
    my_client = AkariSolver()
    filename = r'C:\Users\artur\Desktop\semestre\CMC-15_inteligencia_artificial\labs\akari-solver\doc\example_game0.txt'
    my_client.read_board_from_file(filename)
    result = my_client.solve()
    print(result[0])
    filename = r'C:\Users\artur\Desktop\semestre\CMC-15_inteligencia_artificial\labs\akari-solver\doc\example_game1.txt'
    my_client.read_board_from_file(filename)
    result = my_client.solve()
    print(result[0])
    filename = r'C:\Users\artur\Desktop\semestre\CMC-15_inteligencia_artificial\labs\akari-solver\doc\example_game2.txt'
    my_client.read_board_from_file(filename)
    result = my_client.solve()
    print(result[0])
    filename = r'C:\Users\artur\Desktop\semestre\CMC-15_inteligencia_artificial\labs\akari-solver\doc\example_game3.txt'
    my_client.read_board_from_file(filename)
    result = my_client.solve()
    print(result[0])
