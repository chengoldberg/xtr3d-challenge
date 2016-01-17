import numpy as np
import argparse
import cv2
import math

cv_version = map(int, cv2.__version__.split('.'))
if cv_version[0] != 2 or cv_version[1] != 4 or cv_version[2] < 9:
    raise ImportError('OpenCV version is %s, must be 2.4.x where 9<=x' % cv2.__version__)

class FaceDetector(object):
    """
    This detector looks for a face in a given image over several frames and returns face candidates
    """
    # TODO: Implement this
    pass


class FaceTracker(object):
    """
    This class represents a face candidate that was detected and is now being tracked
    """
    # TODO: Implement this
    pass


class SkinDetector(object):
    """
    Takes an image and a face, and decides
    """
    # TODO: Implement this
    pass


class ForegroundDetector(object):
    """
    Extracts foreground from a given image based on previous frames
    """
    # TODO: Implement this
    pass


class ArmDetector(object):
    """
    Detects an (either left or right) arm based on face, skin and foreground detections
    """

    def __init__(self, side):
        self.side = side

    # TODO: Implement this
    pass


class NUIEngine(object):
    show_debug_window = True

    def __init__(self):
        args = self.parse_cmd_arguments()
        self.playback_video = args.playback_video
        self.record_video = args.record_video
        # Outputs
        self.right_degrees = None
        self.left_degrees = None
        self.face_position = None
        # Video IO
        self.frame_num = -1
        self.video_writer = None
        if self.playback_video:
            self.video_capture = cv2.VideoCapture(self.playback_video)
        else:
            self.video_capture = cv2.VideoCapture(0)
            if self.record_video:
                self.video_writer = cv2.VideoWriter(self.record_video, 0, 30, (640, 480), isColor=True)

    def read_next_frame(self):
        self.frame_num += 1
        res, img = self.video_capture.read()
        if not res:
            raise IOError('Failed to capture next frame')
        if self.video_writer:
            if self.frame_num < 1000:
                self.video_writer.write(img)
            else:
                self.video_writer.release()
                del self.video_writer
        return img

    def preprocess_image(self, img):
        img = cv2.resize(img, (320, 240), interpolation=cv2.INTER_AREA)
        cv2.flip(img, 1, img)
        return img

    def process_image(self, img):
        """
        The main image processing method that takes the input image and finds the output variable if applicable
        :param img:
        :return:
        """
        # TODO: Implement this
        pass

    def show_output_variables(self, img):
        canvas = np.array(img)
        if self.face_position:
            center = np.float32((self.face_position[0]*img.shape[1], self.face_position[1]*img.shape[0]))
            cv2.circle(canvas, tuple(center), 20, (0, 255, 0), thickness=3)
        if self.left_degrees:
            left_vector = np.float32((-np.cos(math.radians(self.left_degrees)), -np.sin(math.radians(self.left_degrees))))
            cv2.line(canvas, tuple(np.uint8(center+left_vector*20)), tuple(np.uint8(center+left_vector*40)), (255, 0, 0), thickness=3)
        if self.right_degrees:
            right_vector = np.float32((np.cos(math.radians(self.right_degrees)), -np.sin(math.radians(self.right_degrees))))
            cv2.line(canvas, tuple(np.uint8(center+right_vector*20)), tuple(np.uint8(center+right_vector*40)), (0, 0, 255), thickness=3)
        cv2.namedWindow("output_img")
        cv2.moveWindow("output_img", 0, 0)
        cv2.imshow("output_img", canvas)
        cv2.waitKey(1)

    def update(self):
        # Reset output variables
        self.right_degrees = None
        self.left_degrees = None
        self.face_position = None

        img = self.read_next_frame()
        img = self.preprocess_image(img)
        self.process_image(img)
        if NUIEngine.show_debug_window:
            self.show_output_variables(img)

    def parse_cmd_arguments(self):
        parser = argparse.ArgumentParser(description='')
        parser.add_argument('-playback-video', dest='playback_video', action='store', required=False, default=None,
                            help='Full path to the video file to playback')
        parser.add_argument('-record-video', dest='record_video', action='store', required=False, default=None,
                            help='Full path to the video file to record')
        return parser.parse_args()


if __name__ == '__main__':
    nui_engine = NUIEngine()
    try:
        while True:
            nui_engine.update()
    except IOError:
        pass
