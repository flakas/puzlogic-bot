import itertools
from z3 import Solver, Int, Or, sat

class Z3Solver:
    def __init__(self):
        pass

    def solve(self, board, pieces, sum_requirements=[]):
        if len(pieces) == 0:
            return []

        solver = Solver()

        # Create z3 variables for each cell
        extended_board = [(row, column, value, Int(self.cell_name(row, column))) for (row, column, value) in board]

        constraints = \
            self.set_prefilled_cell_values(extended_board) + \
            self.set_possible_target_cell_values(extended_board, pieces) + \
            self.require_unique_row_and_column_cells(extended_board) + \
            self.match_sum_requirements(extended_board, sum_requirements) + \
            self.target_cells_use_all_available_pieces(extended_board, pieces)

        for constraint in constraints:
            solver.add(constraint)

        if solver.check() == sat:
            model = solver.model()
            return [
                (row, column, model[cell].as_long())
                    for (row, column, value, cell) in extended_board
                    if self.is_cell_empty(value)
            ]
        else:
            return False

    def set_prefilled_cell_values(self, board):
        return [cell == value for (_, _, value, cell) in board if not self.is_cell_empty(value)]

    def set_possible_target_cell_values(self, board, pieces):
        constraints = []

        for (row, column, value, cell) in board:
            if self.is_cell_empty(value):
                any_of_the_piece_values = [cell == piece for piece in pieces]
                constraints.append(Or(*any_of_the_piece_values))

        return constraints

    def require_unique_row_and_column_cells(self, board):
        return [
            c1 != c2
                for ((x1, y1, _, c1), (x2, y2, _, c2)) in itertools.combinations(board, 2)
                if x1 == x2 or y1 == y2]

    def match_sum_requirements(self, board, sum_requirements):
        constraints = []
        for (dimension, index, target_sum) in sum_requirements:
            relevant_cells = [cell[3] for cell in board if cell[dimension] == index]
            constraints.append(sum(relevant_cells) == target_sum)

        return constraints

    def target_cells_use_all_available_pieces(self, board, pieces):
        empty_cells = [cell for (_, _, value, cell) in board if self.is_cell_empty(value)]
        return [sum(empty_cells) == sum(pieces)]

    def cell_name(self, row, column):
        return 'c_%d_%d' % (row, column)

    def is_cell_empty(self, value):
        return value == 0
