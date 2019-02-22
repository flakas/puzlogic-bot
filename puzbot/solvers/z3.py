import itertools
from z3 import Solver, Int, Or, sat, Distinct, Sum, If
import collections

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
                any_of_the_piece_values = [cell == piece for piece in set(pieces)]
                constraints.append(Or(*any_of_the_piece_values))

        return constraints

    def require_unique_row_and_column_cells(self, board):
        constraints = []
        rows = set([x for (x, _, _, _) in board])
        columns = set([y for (_, y, _, _) in board])

        for row in rows:
            cells = [c for (x, _, _, c) in board if x == row]
            constraints.append(Distinct(*cells))

        for column in columns:
            cells = [c for (_, y, _, c) in board if y == column]
            constraints.append(Distinct(*cells))

        return constraints

    def match_sum_requirements(self, board, sum_requirements):
        constraints = []
        for (dimension, index, target_sum) in sum_requirements:
            relevant_cells = [cell[3] for cell in board if cell[dimension] == index]
            constraints.append(sum(relevant_cells) == target_sum)

        return constraints

    def target_cells_use_all_available_pieces(self, board, pieces):
        constraints = []
        for (piece, quantity) in collections.Counter(pieces).items():
            constraints.append(Sum([If(cell == piece, 1, 0) for (_, _, value, cell) in board if self.is_cell_empty(value)]) == quantity)

        return constraints

    def cell_name(self, row, column):
        return 'c_%d_%d' % (row, column)

    def is_cell_empty(self, value):
        return value == -1
