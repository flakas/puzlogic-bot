import cv2
import numpy as np
import time
import pytesseract
from PIL import Image
from mss import mss

"""
    - Detect game window
    - Create different encapsulated sources for images - either a screenshot, or a file
    - detect start screen of the game ("Press any key")
    - detect level selection screen ("play")
        * Detect individual level locations
        * Detect where a level needs to be dragged
    - Level screen
        * Detect cells in board
        * Parse numbers within cells
        * Parse available pieces
    - Detect "Level completed" screen
        * Find location of "Next" button

"""

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
        sct_img = self.screen.grab(self.monitor)
        img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
        img = np.array(img)
        img = self.convert_rgb_to_bgr(img)

        return img

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
        """ Detects location of the game board and returns it """
        img = self.source.get()
        img_final = img.copy()
        img2gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find black background around the game screen
        ret, mask = cv2.threshold(img2gray, 1, 255, cv2.THRESH_BINARY)
        new_img = cv2.bitwise_not(mask)
        '''
            Remove noisy portion
        '''
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,
                                                             3))  # to manipulate the orientation of dilution , large x means horizonatally dilating  more, large y means vertically dilating more
        dilated = cv2.dilate(new_img, kernel, iterations=1)  # dilate , more the iteration more the dilation

        im2, contours, hierarchy = cv2.findContours(dilated, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)  # get contours

        for contour in contours:
            # get rectangle bounding contour
            [x, y, w, h] = cv2.boundingRect(contour)

            # Discard small pieces, we're looking for a game window 800x800
            if w < 700 or h < 500 or w > 800:
                continue

            # draw rectangle around contour on original image
            # cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), 2)

            cropped = img_final[y:y+h, x:x+w]

            return (x, y, w, h, cropped)

        return False

    @cache_until_refresh
    def get_pieces(self):
        cells = self.get_visible_cells()

        lowest_cell = max(cells, key=lambda c: c[1])

        return list(filter(lambda c: abs(lowest_cell[1] - c[1]) < lowest_cell[3]*3, cells))

    @cache_until_refresh
    def get_cells(self):
        cells = self.get_visible_cells()

        pieces = self.get_pieces()

        return list(set(cells) - set(pieces))

    @cache_until_refresh
    def get_visible_cells(self):
        (x, y, w, h, img) = self.get_game_board()

        img2gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        ret, mask = cv2.threshold(img2gray, 100, 255, cv2.THRESH_BINARY)
        new_img = cv2.bitwise_not(mask)

        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,
                                                             3))  # to manipulate the orientation of dilution , large x means horizonatally dilating  more, large y means vertically dilating more
        dilated = cv2.dilate(new_img, kernel, iterations=1)  # dilate , more the iteration more the dilation

        im2, contours, hierarchy = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # get contours

        # [x, y, w, h, img]
        contours = map(lambda c: list(cv2.boundingRect(c)), contours)
        candidates = filter(lambda c: 40 < c[2] < 60 and 40 < c[3] < 60, contours)
        cells = map(lambda c: tuple(list(c[0:4]) + [self._recognize_number(img[c[1]:c[1]+c[3], c[0]:c[0]+c[2]])]), candidates)
        return list(cells)

        # for contour in candidates:
            # [x, y, w, h, c] = contour
            # cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), 2)

        # return img

    @cache_until_refresh
    def get_constraints(self):
        return []

    def _recognize_number(self, img):
        img = img[5:-5, 5:-5]
        img2gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        ret, mask = cv2.threshold(img2gray, 100, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        new_img = cv2.bitwise_not(mask)

        new_img = cv2.medianBlur(new_img, 3)

        # Turn white text \w black background into black text \w white background
        if new_img[0, 0] == 0:
            new_img = cv2.bitwise_not(new_img)

        # cv2.imshow('grayscale', new_img)
        # cv2.waitKey()
        # print(pytesseract.image_to_string(new_img, config='--psm 10'))
        character = pytesseract.image_to_string(new_img, config='--psm 10')
        try:
            return int(character)
        except:
            # print(character)
            return False

    def debug(self):
        start = time.time()
        # res = self.get_pieces()
        # cv2.imshow('grayscale', res)
        # cv2.waitKey()
        for cell in self.get_pieces():
            print(cell)

        for cell in self.get_cells():
            print(cell)

        print('Ended at', time.time() - start)
