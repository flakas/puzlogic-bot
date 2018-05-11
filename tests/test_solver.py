import unittest

from puzbot.solver import Solver

class TestSolver(unittest.TestCase):

    def setUp(self):
        self.solver = Solver()

    def test_it_initializes(self):
        solver = Solver()

    def test_unfilled_board_is_legal(self):
        board = [
            (0, 1, 1),
            (1, 0, 0),
            (1, 1, 0),
            (2, 0, 2)
        ]
        self.assertTrue(self.solver.is_legal(board, []))

    def test_board_with_duplicates_is_illegal(self):
        board = [
            (0, 1, 1),
            (1, 0, 0),
            (1, 1, 1),
            (2, 0, 2)
        ]
        self.assertFalse(self.solver.is_legal(board, []))

    def test_board_with_matching_constraints_is_legal(self):
        board = [
            (0, 1, 1),
            (1, 0, 0),
            (1, 1, 2),
            (2, 0, 2)
        ]

        constraints = [
            (1, 1, 3)
        ]

        self.assertTrue(self.solver.is_legal(board, constraints))

    def test_board_with_higher_sum_fails_constraint(self):
        board = [
            (0, 1, 1),
            (1, 0, 0),
            (1, 1, 3),
            (2, 0, 2)
        ]

        constraints = [
            (1, 1, 3)
        ]

        self.assertFalse(self.solver.is_legal(board, constraints))

    def test_board_with_unfilled_fields_and_lower_sum_is_legal(self):
        board = [
            (0, 1, 1),
            (1, 0, 0),
            (1, 1, 2),
            (2, 0, 2)
        ]

        constraints = [
            (0, 1, 3)
        ]
        self.assertTrue(self.solver.is_legal(board, constraints))

    def test_rows(self):
        board = [
            (0, 1, 1),
            (1, 0, 0),
            (1, 1, 0),
            (2, 0, 2)
        ]

        rows = self.solver.rows(board)
        self.assertEqual(rows[0], [1])
        self.assertEqual(rows[1], [0, 0])
        self.assertEqual(rows[2], [2])

    def test_columns(self):
        board = [
            (0, 1, 1),
            (1, 0, 0),
            (1, 1, 0),
            (2, 0, 2)
        ]

        columns = list(self.solver.columns(board))

        print(list(columns[1]))
        self.assertEqual(columns[0], [0, 2])
        self.assertEqual(columns[1], [1, 0])

    def test_filled_cells_removes_unfilled_cells(self):
        self.assertEqual(
            list(self.solver.filled_cells([0, 1, 2, 0])),
            [1, 2]
        )

    def test_includes_all_legal_moves(self):
        board = [
            (0, 1, 1),
            (1, 0, 0),
            (1, 1, 0),
            (2, 0, 2)
        ]
        pieces = [1, 2]

        all_moves = list(self.solver.legal_moves(board, pieces, []))
        game_moves = set([move[0] for move in all_moves])

        self.assertEquals(len(game_moves), 2)
        self.assertIn((1, 0, 1), game_moves)
        self.assertIn((1, 1, 2), game_moves)

    def test_includes_all_moves(self):
        board = [
            (0, 1, 1),
            (1, 0, 0),
            (1, 1, 0),
            (2, 0, 2)
        ]
        pieces = [1, 2]

        all_moves = list(self.solver.all_moves(board, pieces, []))
        game_moves = set([move[0] for move in all_moves])

        self.assertIn((1, 0, 1), game_moves)
        self.assertIn((1, 0, 2), game_moves)
        self.assertIn((1, 1, 1), game_moves)
        self.assertIn((1, 1, 2), game_moves)

    def test_move_adds_piece_to_board(self):
        board = [
            (0, 1, 1),
            (1, 0, 0),
            (1, 1, 0),
            (2, 0, 2)
        ]
        pieces = [1]

        (new_board, new_pieces, constraints) = self.solver.perform_move((1, 0, 1), board, pieces, [])

        self.assertIn((1, 0, 1), new_board)

    def test_move_removes_piece_from_pieces(self):
        board = [
            (0, 1, 1),
            (1, 0, 0),
            (1, 1, 0),
            (2, 0, 2)
        ]
        pieces = [1, 1, 2]

        (new_board, new_pieces, constraints) = self.solver.perform_move((1, 0, 1), board, pieces, [])

        self.assertEquals(new_pieces, [1, 2])

    def test_solution(self):
        board = [
            (0, 1, 1),
            (1, 0, 0),
            (1, 1, 0),
            (2, 0, 2)
        ]
        pieces = [1, 2]

        moves = list(self.solver.solve(board, pieces, []))

        self.assertEquals(moves, [(1, 0, 1), (1, 1, 2)])

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
        self.assertIn((0, 0, 4), moves)
        self.assertIn((0, 2, 6), moves)
        self.assertIn((1, 3, 5), moves)
        self.assertIn((2, 4, 4), moves)
        self.assertIn((3, 1, 5), moves)
        self.assertIn((4, 4, 6), moves)
