import cv2
import numpy as np
from detector import Detector
from tracker import Tracker
from shape import ShapeType
from utils import get_object_color, convert_to_qimage, calculate_rectangle_area, calculate_circle_area
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage

class VideoProcessorWorker(QThread):
    """
        Worker thread for processing the video, manages the Detector and Tracker classes.
    """
    def __init__(self, video_path: str):
        super().__init__()
        self.video_path = video_path

    # signals as class attributes
    shapes_updated = pyqtSignal(list)
    image_updated = pyqtSignal(QImage)
    frame_updated = pyqtSignal(QImage)
    processing_finished = pyqtSignal()

    def run(self) -> None:
        cap = cv2.VideoCapture(self.video_path)
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        trajectory_image = np.zeros((height, width, 3), dtype=np.uint8)

        # minimum areas for preventing FP's detections, not good idea if we want to detect small shapes (not this case)
        min_rectangle_area = 1200
        min_circle_area = 1000

        detector = Detector()
        tracker = Tracker(trajectory_image)

        frame_id = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_shapes = [] # store the detected shapes in the current frame

            circles = detector.detect_circles(frame)
            rectangles = detector.detect_rectangles(frame)

            if circles is not None:
                for (x, y, r) in circles:
                    area = calculate_circle_area((x, y, r))
                    detected_shape = {
                        "shape_type": ShapeType.CIRCLE,
                        "bounding": (x, y, r),
                        "center": (x, y),
                        "color": get_object_color(frame, (x, y))
                    }
                    if area >= min_circle_area:
                        frame_shapes.append(detected_shape)

            if rectangles is not None:
                for (x1, y1, x2, y2) in rectangles:
                    area = calculate_rectangle_area(((x1, y1), (x2, y2)))
                    detected_shape = {
                        "shape_type": ShapeType.RECTANGLE,
                        "bounding": ((x1, y1), (x2, y2)),
                        "center": ((x1 + x2) // 2, (y1 + y2) // 2),
                        "color": get_object_color(frame, ((x1 + x2) // 2, (y1 + y2) // 2))
                    }
                    if area >= min_rectangle_area:
                        frame_shapes.append(detected_shape)

            # pass detected shapes to the tracker to handle the tracking and drawing
            tracked_shapes = tracker.new_frame(frame_id, frame, frame_shapes)            

            # signal the updated shapes to the main thread
            self.shapes_updated.emit(tracked_shapes)
 
            # convert trajectory image and frame to QImage and signal them to the main thread
            qimage_trajectory = convert_to_qimage(trajectory_image)
            qimage_frame = convert_to_qimage(frame)
            self.image_updated.emit(qimage_trajectory)
            self.frame_updated.emit(qimage_frame)

            frame_id += 1

        cap.release()
        self.processing_finished.emit()