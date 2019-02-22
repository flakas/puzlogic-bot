import cv2
import numpy as np
import time
import pytesseract
from PIL import Image
from mss import mss
from collections import namedtuple
import os
import imutils
import itertools

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
    def __init__(self, source, templates_path=''):
        self.source = source
        self.templates_path = templates_path
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

        # contour_image_target = screen_image.copy()
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
        lowest_cell = max(cells, key=lambda c: c.y)

        # Expect available pieces to be lower than the lowest row of game board cells
        return list(filter(lambda c: abs(lowest_cell.y - c.y) < lowest_cell.h*3, cells))

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

        # kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (2, 2))
        # dilated = cv2.dilate(binary_grayscale, kernel, iterations=1)
        dilated = binary_grayscale

        _, contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        Cell = namedtuple('Cell', ['x', 'y', 'w', 'h', 'content'])

        # [x, y, w, h, img]
        bounding_boxes = map(lambda c: list(cv2.boundingRect(c)), contours)
        candidates = filter(lambda b: 30 < b[2] < 50 and 30 < b[3] < 50, bounding_boxes)
        cells = map(lambda c: Cell(c[0], c[1], c[2], c[3], self._recognize_number(board.screen[c[1]:c[1]+c[3], c[0]:c[0]+c[2]])), candidates)
        result = list(cells)

        board_original = board.screen.copy()
        board_dilated = cv2.cvtColor(dilated.copy(), cv2.COLOR_GRAY2BGR)

        for (x, y, w, h, cell_image) in result:
            cv2.rectangle(board_original, (x, y), (x+w, y+h), (0, 0, 255), 2)
            cv2.rectangle(board_dilated, (x, y), (x+w, y+h), (0, 0, 255), 2)

        return result

    @cache_until_refresh
    def get_constraints(self):
        template = os.path.join(self.templates_path, 'target-sum-indicator.png')
        template = cv2.imread(template)
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        ret, mask = cv2.threshold(template, 100, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        template = cv2.bitwise_not(mask)

        rotations = [self._rotate(template, angle) for angle in [0, 90, 180, 270]]

        board = self.get_game_board()
        grayscale = cv2.cvtColor(board.screen, cv2.COLOR_BGR2GRAY)
        ret, mask = cv2.threshold(grayscale, 100, 255, cv2.THRESH_BINARY)
        grayscale_board = cv2.bitwise_not(mask)

        matches = [self.match_template(grayscale_board, template, 0.8) for template in rotations]
        [left, top, right, bottom] = matches
        left = left if left is not None else []
        top = top if top is not None else []
        right = right if right is not None else []
        bottom = bottom if bottom is not None else []

        return \
            [self.parse_target_sums(board, 'row', item, -32, -15, 32, 42) for item in left] + \
            [self.parse_target_sums(board, 'column', item, -15, -32, 42, 32) for item in top] + \
            [self.parse_target_sums(board, 'row', item, 8, -15, 32, 42) for item in right] + \
            [self.parse_target_sums(board, 'column', item, -15, 8, 42, 32) for item in bottom]


    def parse_target_sums(self, board, orientation, cell, x_offset, y_offset, width, height):
        x = cell[1] + x_offset
        y = cell[0] + y_offset
        if x < 0: x = 0
        if y < 0: y = 0

        original = board.screen.copy()
        cv2.rectangle(original, (x, y), (x+width, y+height), (0, 0, 255), 3)
        constraint_cell = board.screen[y:y+height, x:x+width]
        target_sum = int(self._recognize_target_sum(constraint_cell))

        indexes = (y, x)
        dimension = 0 if orientation == 'row' else 1
        index = indexes[dimension]

        return (dimension, index, target_sum)

    def _rotate(self, img, angle):
        return imutils.rotate_bound(img, angle)

    def match_template(self, img_grayscale, template, threshold=0.9):
        """
        Matches template image in a target grayscaled image
        """

        res = cv2.matchTemplate(img_grayscale, template, cv2.TM_CCOEFF_NORMED)
        matches = np.where(res >= threshold)
        matches = np.transpose(matches)
        if not np.size(matches):
            return None
        return matches

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

    def _recognize_target_sum(self, image):
        borderless_image = image
        # Scale up cells to make it easier for tesseract to OCR them
        scaling_factor = 2

        grayscale = cv2.cvtColor(borderless_image, cv2.COLOR_BGR2GRAY)

        ret, mask = cv2.threshold(grayscale, 150, 255, cv2.THRESH_BINARY)
        binary_grayscale = cv2.bitwise_not(mask)

        ocr_image = binary_grayscale
        ocr_image = cv2.GaussianBlur(ocr_image, (3, 3), 0)
        ocr_image = cv2.resize(
            ocr_image,
            (
                int(ocr_image.shape[1]) * scaling_factor,
                int(ocr_image.shape[0]) * scaling_factor
            )
        )

        if ocr_image[0, 0] == 0:
            # OCR needs black text on white background
            black_text_on_white_background = cv2.bitwise_not(ocr_image)
            ocr_image = black_text_on_white_background


        # Single text line mode
        number = pytesseract.image_to_string(ocr_image, config='--psm 7')
        try:
            return int(number)
        except:
            return False
