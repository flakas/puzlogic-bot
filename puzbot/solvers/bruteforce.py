import itertools

class BruteForceSolver:
    def __init__(self):
        pass

    def solve(self, board, pieces, constraints=[]):
        if len(pieces) == 0:
            return []

        for (move, new_board, new_pieces, new_constraints) in self.legal_moves(board, pieces, constraints):
            solution = self.solve(new_board, new_pieces, new_constraints)
            if solution != False:
                return [move] + solution

        return False

    def is_legal(self, board, constraints):
        """
        Is the board legal.
        - Rows and columns contain no duplicates
        - If there are constraints and all cells are filled in a given column - the sum of the column does not exceed the constraint
        - If all cells are filled in - constraint matches
        """

        lines = self.rows(board) + self.columns(board)

        no_duplicates = all(self.all_unique(self.filled_cells(line)) for line in lines)
        satisfies_constraints = all(self.satisfies_constraint(board, c) for c in constraints)

        return no_duplicates and satisfies_constraints

    def legal_moves(self, board, pieces, constraints):
        return (move for move in self.all_moves(board, pieces, constraints) if self.is_legal(move[1], constraints))

    def all_moves(self, board, pieces, constraints):
        """ Attempt to put one of available pieces into the available spaces on the board """
        free_cells = [(c[0], c[1]) for c in board if c[2] == 0]
        return (
            ((row, column, piece), new_board, new_pieces, constraints)
            for (row, column) in free_cells
            for piece in pieces
            for (new_board, new_pieces, new_constraints) in [self.perform_move((row, column, piece), board, pieces, constraints)]
        )

    def perform_move(self, move, board, pieces, constraints):
        """ Moves the given piece to the location on the board """
        new_pieces = pieces.copy()
        new_pieces.remove(move[2])

        new_board = board.copy()
        new_board.remove((move[0], move[1], 0))
        new_board.append(move)

        return new_board, new_pieces, constraints

    def rows(self, board):
        return self._lines(board, 0)

    def columns(self, board):
        return self._lines(board, 1)

    def _lines(self, board, dimension=0):
        discriminator = lambda c: c[dimension]
        cells = sorted(board, key=discriminator)
        groups = itertools.groupby(cells, key=discriminator)
        return [[c[2] for c in group] for index, group in groups]

    def filled_cells(self, line):
        return [x for x in line if x != 0]

    def all_unique(self, line):
        return len(line) == len(set(line))

    def all_cells_filled(self, line):
        return len(self.filled_cells(line)) == len(line)

    def satisfies_constraint(self, board, constraint):
        (dimension, element, target_sum) = constraint
        line = self._lines(board, dimension)[element]
        line_sum = sum(line)
        return (
            (line_sum == target_sum and self.all_cells_filled(line))
            or
            (line_sum < target_sum)
        )
