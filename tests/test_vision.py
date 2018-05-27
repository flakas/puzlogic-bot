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
