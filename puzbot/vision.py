import cv2
import numpy as np
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
        if not self.image:
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

class Vision:
    def __init__(self, source):
        self.source = source

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
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), 2)

            cropped = img_final[y:y+h, x:x+w]

            return (x, y, w, h, cropped)

        return False

    def debug(self):
        res = self.get_game_board()
        cv2.imshow('grayscale', res[4])
        cv2.waitKey()

    def find_text(self):
        img = self.source.get()

        img_final = img.copy()
        img2gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, mask = cv2.threshold(inverted, 180, 255, cv2.THRESH_BINARY)
        image_final = cv2.bitwise_and(img2gray, img2gray, mask=mask)
        ret, new_img = cv2.threshold(image_final, 60, 255, cv2.THRESH_BINARY)  # for black text , cv.THRESH_BINARY_INV
        '''
                line  8 to 12  : Remove noisy portion 
        '''
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,
                                                             3))  # to manipulate the orientation of dilution , large x means horizonatally dilating  more, large y means vertically dilating more
        dilated = cv2.dilate(new_img, kernel, iterations=9)  # dilate , more the iteration more the dilation

        # for cv2.x.x

        # results = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # get contours
        # print(len(results))
        im2, contours, hierarchy = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # get contours

        # for cv3.x.x comment above line and uncomment line below

        #image, contours, hierarchy = cv2.findContours(dilated,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)


        for contour in contours:
            # get rectangle bounding contour
            [x, y, w, h] = cv2.boundingRect(contour)

            # Don't plot small false positives that aren't text
            if w < 5 and h < 5:
                continue

            # draw rectangle around contour on original image
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), 2)

            '''
            #you can crop image and send to OCR  , false detected will return no text :)
            cropped = img_final[y :y +  h , x : x + w]

            s = file_name + '/crop_' + str(index) + '.jpg' 
            cv2.imwrite(s , cropped)
            index = index + 1

            '''
        # write original image with added contours to disk
        cv2.imshow('captcha_result', img)
        cv2.imshow('grayscale', new_img)
        cv2.waitKey()
