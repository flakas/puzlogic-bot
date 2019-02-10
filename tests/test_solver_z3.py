import unittest

from puzbot.solvers.z3 import Z3Solver

class TestZ3Solver(unittest.TestCase):

    def setUp(self):
        self.solver = Z3Solver()

    def test_it_initializes(self):
        solver = Z3Solver()

    def test_solution_solves_the_puzzle_first(self):
        board = [
            (0, 1, 1),
            (1, 0, 0),
            (1, 1, 0),
            (2, 0, 2)
        ]
        pieces = [1, 2]

        moves = list(self.solver.solve(board, pieces, []))

        self.assertEquals(moves, [(1, 0, 1), (1, 1, 2)])

    def test_solution_solves_the_puzzle_third(self):
        board = [
            (0, 0, 0),
            (0, 2, 0),
            (0, 4, 5),
            (1, 1, 4),
            (1, 3, 0),
            (2, 0, 6),
            (2, 4, 0),
            (3, 1, 0),
            (3, 3, 6),
            (4, 0, 5),
            (4, 2, 4),
            (4, 4, 0),
        ]
        pieces = [4, 5, 6, 4, 5, 6]

        moves = list(self.solver.solve(board, pieces, []))

        self.assertEquals(len(moves), 6)
        moves = set(moves)
        print(moves)
        self.assertIn((0, 0, 4), moves)
        self.assertIn((0, 2, 6), moves)
        self.assertIn((1, 3, 5), moves)
        self.assertIn((2, 4, 4), moves)
        self.assertIn((3, 1, 5), moves)
        self.assertIn((4, 4, 6), moves)

    def test_solution_solves_the_puzzle_seventh(self):
        board = [
            (0, 0, 2),
            (0, 3, 0),
            (0, 5, 0),
            (1, 0, 0),
            (1, 1, 1),
            (1, 4, 5),
            (1, 5, 0),
            (2, 0, 6),
            (2, 2, 4),
            (2, 5, 0),
            (3, 0, 0),
            (3, 3, 3),
            (3, 5, 8),
            (4, 2, 0),
            (4, 3, 0),
            (4, 4, 7)
        ]

        pieces = [1, 2, 3, 4, 5, 6, 7, 8]

        constraints = [
            (0, 0, 14),
            (0, 1, 15),
            (1, 0, 18),
            (1, 3, 13),
            (1, 5, 19)
        ]

        moves = list(self.solver.solve(board, pieces, constraints))

        self.assertEquals(len(moves), 8)
        moves = set(moves)
        print(moves)
        self.assertIn((0, 3, 8), moves)
        self.assertIn((0, 5, 4), moves)
        self.assertIn((1, 0, 3), moves)
        self.assertIn((1, 5, 6), moves)
        self.assertIn((2, 5, 1), moves)
        self.assertIn((3, 0, 7), moves)
        self.assertIn((4, 2, 5), moves)
        self.assertIn((4, 3, 2), moves)

