import cv2
import random
import numpy as np
from shape import Shape
from PyQt5.QtGui import QImage

# initial idea was to use some kind of random unique id, but it is overkill for this task, there are just few shapes
def generate_unique_id(length=10) -> int:
    min_value = 10**(length - 1)
    max_value = 10**length - 1
    return random.randint(min_value, max_value)

# from task_description.md: "Any detection or tracking mistakes should be easily identifiable.",
# so split history is needed, so I dont just interpolate between the None values that are caused by detection mistakes such as overlapping shapes
def split_history(history: list) -> list:
    segments = []
    segment = []

    none_count = 0
    for pt in history:
        if pt[-1] is None:
            none_count += 1
        else:
            if none_count > 10: # arbitrary number, if there are more than 10 None values, it is probably due to overlapping shapes, so we split the history
                if segment:
                    segments.append(segment)
                segment = []
            none_count = 0
            segment.append(pt)

    if segment:
        segments.append(segment)

    return segments

def calculate_rectangle_area(rectangle: tuple) -> int:
    (x1, y1), (x2, y2) = rectangle
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    return width * height

# probably overkill making function for this
def calculate_circle_area(circle: tuple) -> int:
    x, y, r = circle
    return np.pi * r * r

def euclidean_distance(point1: int, point2: int) -> float:
    return np.linalg.norm(np.array(point1) - np.array(point2))

def color_distance(color1: tuple, color2: tuple) -> float:
    # normalize color values and compute the distance
    color1 = np.array(color1) / 255.0
    color2 = np.array(color2) / 255.0
    return np.linalg.norm(color1 - color2)

def match_shape(new_shape: dict, existing_shapes: list, max_distance=100, max_color_distance=0.15) -> Shape | None:
    for existing_shape in existing_shapes:

        # get the last valid (non-None) center from the shape's history
        # the None values represent frames where the shape was not detected (on the edges of screen or overlapped, etc..)
        last_valid_center = next((center for center in reversed(existing_shape.history) if center[-1] is not None), None)

        if last_valid_center is not None: # needed bcs next defaults to None if not found
            if (
                new_shape["shape_type"] == existing_shape.shape_type and
                color_distance(new_shape["color"], existing_shape.color) < max_color_distance and
                euclidean_distance(new_shape["center"], last_valid_center[-1]) < max_distance
            ):
                return existing_shape
    return None

def get_object_color(frame: np.ndarray, center: tuple) -> tuple:
    b, g, r = frame[center[1], center[0]]
    return (r, g, b)  # returning color as RGB

def convert_to_qimage(image: np.ndarray) -> QImage:
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width, channel = image_rgb.shape
    bytes_per_line = 3 * width # 3 for RGB
    return QImage(image_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)