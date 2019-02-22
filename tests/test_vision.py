import unittest

from puzbot.vision import Vision, ImageFileSource

class TestVision(unittest.TestCase):

    def setUp(self):
        self.source = ImageFileSource('tests/screenshots/puzlogic-level-completed.png')
        self.vision = Vision(self.source)

    def test_it_finds_the_game_board(self):
        (x, y, width, height, img) = self.vision.get_game_board()

        self.assertGreater(x, 0)
        self.assertGreater(y, 0)
        self.assertEqual(width, 800)
        self.assertEqual(height, 600)

    def test_it_finds_pieces_in_one_row(self):
        source = ImageFileSource('tests/screenshots/puzlogic-map-1.png')
        vision = Vision(source)

        self.assertEqual(len(vision.get_pieces()), 2)

    def test_it_finds_pieces_in_multiple_rows(self):
        source = ImageFileSource('tests/screenshots/puzlogic-map-3.png')
        vision = Vision(source)

        self.assertEqual(len(vision.get_pieces()), 6)

    def test_it_recognizes_digit(self):
        source = ImageFileSource('tests/screenshots/single-piece.png')
        vision = Vision(source)

        self.assertEqual(vision._recognize_number(source.get()), 3)

    def test_it_recognizes_constraint(self):
        target_sums = {
            'tests/screenshots/constraint_cell_13.png': 13,
            'tests/screenshots/constraint_cell_19.png': 19,
            'tests/screenshots/constraint_cell_04.png': 4,
            'tests/screenshots/constraint_cell_11.png': 11,
        }

        for (filename, target) in target_sums.items():
            source = ImageFileSource(filename)
            vision = Vision(source, templates_path='templates/')

            self.assertEqual(vision._recognize_target_sum(source.get()), target)

    def test_it_finds_constraints(self):
        source = ImageFileSource('tests/screenshots/puzlogic-with-sums.png')
        vision = Vision(source, templates_path='templates/')

        found_constraints = vision.get_constraints()

        self.assertEqual(len(found_constraints), 3)

    def test_it_find_constraints_within_level_9(self):
        source = ImageFileSource('tests/screenshots/puzlogic-map-9.png')
        vision = Vision(source, templates_path='templates/')

        found_constraints = vision.get_constraints()

        self.assertEqual(len(found_constraints), 2)
        self.assertIn((0, 38, 4), found_constraints)
        self.assertIn((0, 182, 6), found_constraints)
