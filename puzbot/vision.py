import cv2
import numpy as np
import time
import pytesseract
from PIL import Image
from mss import mss
from collections import namedtuple

class ImageFileSource:
    def __init__(self, path):
        self.path = path

    def get(self):
        return cv2.imread(self.path)

class ScreenshotSource:
    def __init__(self):
        self.monitor = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
        self.screen = mss()
        self.image = None

    def get(self):
        if self.image is None:
            self.image = self.refresh()

        return self.image

    def refresh(self):
        source_image = self.screen.grab(self.monitor)
        rgb_image = Image.frombytes('RGB', source_image.size, source_image.rgb)
        rgb_image = np.array(rgb_image)
        bgr_image = self.convert_rgb_to_bgr(rgb_image)

        return bgr_image

    def convert_rgb_to_bgr(self, img):
        return img[:, :, ::-1]

def cache_until_refresh(func):
    def wrapper(self):
        if func in self.cache:
            return self.cache[func]

        result = func(self)
        self.cache[func] = result
        return result

    return wrapper

class Vision:
    def __init__(self, source):
        self.source = source
        self.cache = {}

    def refresh(self):
        self.cache = {}
        self.source.refresh()

    @cache_until_refresh
    def get_game_board(self):
        """ Detects the game window area within a computer screen """

        screen_image = self.source.get()
        original_screen_image = screen_image.copy()
        grayscale = cv2.cvtColor(screen_image, cv2.COLOR_BGR2GRAY)

        # Find black background around the game screen
        ret, mask = cv2.threshold(grayscale, 1, 255, cv2.THRESH_BINARY)
        binary_grayscale = cv2.bitwise_not(mask)

        # Eliminate noise and smaller elements
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
        dilated = cv2.dilate(binary_grayscale, kernel, iterations=1)

        _, contours, _ = cv2.findContours(dilated, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        Board = namedtuple('Board', ['x', 'y', 'w', 'h', 'screen'])

        for contour in contours:
            # get rectangle bounding contour
            [x, y, w, h] = cv2.boundingRect(contour)

            # Discard small pieces, we're looking for a game window roughly 800x600
            if w < 700 or h < 500 or w > 800:
                continue

            cropped = original_screen_image[y:y+h, x:x+w]

            return Board(x, y, w, h, cropped)

        return False

    @cache_until_refresh
    def get_pieces(self):
        cells = self.get_visible_cells()
        lowest_cell = max(cells, key=lambda c: c[1])

        # Expect available pieces to be lower than the lowest row of game board cells
        return list(filter(lambda c: abs(lowest_cell[1] - c[1]) < lowest_cell[3]*3, cells))

    @cache_until_refresh
    def get_cells(self):
        cells = self.get_visible_cells()
        pieces = self.get_pieces()

        return list(set(cells) - set(pieces))

    @cache_until_refresh
    def get_visible_cells(self):
        board = self.get_game_board()

        grayscale = cv2.cvtColor(board.screen, cv2.COLOR_BGR2GRAY)

        ret, mask = cv2.threshold(grayscale, 100, 255, cv2.THRESH_BINARY)
        binary_grayscale = cv2.bitwise_not(mask)

        # Erase smaller artifacts on screen, hopefully leaving only
        # larger contours to detect.
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
        dilated = cv2.dilate(binary_grayscale, kernel, iterations=1)

        _, contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # [x, y, w, h, img]
        bounding_boxes = map(lambda c: list(cv2.boundingRect(c)), contours)
        candidates = filter(lambda b: 40 < b[2] < 60 and 40 < b[3] < 60, bounding_boxes)
        cells = map(lambda c: tuple(list(c[0:4]) + [self._recognize_number(board.screen[c[1]:c[1]+c[3], c[0]:c[0]+c[2]])]), candidates)
        return list(cells)

    @cache_until_refresh
    def get_constraints(self):
        # TODO: add constraint identification
        return []

    def _recognize_number(self, candidate_tile_image):
        """ Attempts to OCR the number within a game tile image """

        borderless_image = candidate_tile_image[5:-5, 5:-5]
        grayscale = cv2.cvtColor(borderless_image, cv2.COLOR_BGR2GRAY)

        ret, mask = cv2.threshold(grayscale, 100, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        binary_grayscale = cv2.bitwise_not(mask)

        # Blur to help text show up better for OCR
        ocr_image = cv2.medianBlur(binary_grayscale, 3)

        if ocr_image[0, 0] == 0:
            # OCR needs black text on white background
            black_text_on_white_background = cv2.bitwise_not(ocr_image)
            ocr_image = black_text_on_white_background

        # Use single-character segmentation mode for Tesseract
        character = pytesseract.image_to_string(ocr_image, config='--psm 10')
        try:
            return int(character)
        except:
            return False
