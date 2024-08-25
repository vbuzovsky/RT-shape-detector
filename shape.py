from enum import Enum

class ShapeType(Enum):
    CIRCLE = "circle"
    RECTANGLE = "rectangle"

class Shape:
    def __init__(self, shape_id: int, shape_type: ShapeType, bounding: tuple, center: tuple, color: tuple, first_occurence: int) -> None:
        self.id = shape_id
        self.shape_type = shape_type
        self.bounding = bounding
        self.center = center 
        self.color = color
        # list of center points of the shape during its existence, with the frame ID as the first element
        self.history = [(first_occurence, center)] 