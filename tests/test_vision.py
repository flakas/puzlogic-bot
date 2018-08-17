import unittest

from puzbot.vision import Vision, ImageFileSource

class TestSolver(unittest.TestCase):

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

    def test_it_finds_pieces_in_multiple_row(self):
        source = ImageFileSource('tests/screenshots/puzlogic-map-3.png')
        vision = Vision(source)

        self.assertEqual(len(vision.get_pieces()), 6)

    def test_it_recognizes_digit(self):
        source = ImageFileSource('tests/screenshots/single-piece.png')
        vision = Vision(source)

        self.assertEqual(vision._recognize_number(source.get()), 3)
