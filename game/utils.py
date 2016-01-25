import os
import cv2


class ImageSequenceReader:

    def __init__(self, images_path, fps):
        self.images_path = images_path
        self.fps = fps
        self.images = os.listdir(images_path)
        self.frame = 0
        self.cnt = 0

    def read(self):
        img = cv2.imread(os.path.join(self.images_path, self.images[self.frame]))
        if self.cnt == self.fps:
            self.frame += 1
            self.frame %= len(self.images)
            self.cnt = 0
        self.cnt += 1
        return True, img
