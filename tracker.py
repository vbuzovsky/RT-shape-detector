import cv2
import numpy as np
from utils import match_shape, split_history
from shape import Shape, ShapeType


class Tracker:
    """ 
        Class that manages all the tracking and drawing of shapes on the frame and trajectory image.

        Parameters
        ----------
        trajectory_image : np.array
            Image where the trajectory of the shapes will be drawn.

        Methods
        -------
        new_frame(frame_id, frame, detected_shapes) -> list
            Update the tracked shapes with new detections, return the updated list of tracked shapes.

        draw_shape_on_frame(shape, frame) -> None
            Draw the bounding box and ID of the shape on the frame.

        draw_shape_path(shape, trajectory_image) -> None
            Draw the path of the shape on the trajectory image.
    """
    def __init__(self, trajectory_image: np.ndarray) -> None:
        self.trajectory_image = trajectory_image
        self.tracked_shapes = []
        self.id_counter = 1

    def new_frame(self, frame_id: int, frame: np.ndarray, detected_shapes: list) -> list:
        current_tracked_ids = set()

        for shape in detected_shapes:
            existing_shape = match_shape(shape, self.tracked_shapes)

            if existing_shape:
                existing_shape.center = shape["center"]
                existing_shape.bounding = shape["bounding"]
                existing_shape.history.append((frame_id, existing_shape.center))

                self._draw_shape_on_frame(existing_shape, frame)
                self._draw_shape_path(existing_shape, self.trajectory_image)
                current_tracked_ids.add(existing_shape.id)
            else:
                new_shape = Shape(
                    shape_id=self.id_counter,
                    shape_type=shape["shape_type"],
                    bounding=shape["bounding"],
                    center=shape["center"],
                    color=shape["color"],
                    first_occurence=frame_id
                    )
                self.tracked_shapes.append(new_shape)
                current_tracked_ids.add(self.id_counter)
                self.id_counter += 1

                self._draw_shape_on_frame(new_shape, frame)

        for tracked_shape in self.tracked_shapes:
            if tracked_shape.id not in current_tracked_ids:
                tracked_shape.history.append((frame_id, None))
            
        return self.tracked_shapes
    
    def _draw_shape_on_frame(self, shape: Shape, frame: np.ndarray) -> None:
        """ Draw the bounding box and ID on the frame. """
        if shape.shape_type == ShapeType.CIRCLE:
            x, y, r = shape.bounding
            cv2.circle(frame, (x, y), r, (0, 255, 0), 2)  # green circle
            cv2.circle(frame, shape.center, 3, (0, 0, 255), -1)  # ged center point
            cv2.putText(frame, f'ID: {shape.id}', (x + r + 5, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        elif shape.shape_type == ShapeType.RECTANGLE:
            (x1, y1), (x2, y2) = shape.bounding
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # green rectangle
            cv2.circle(frame, shape.center, 3, (0, 0, 255), -1)  # red center point
            cv2.putText(frame, f'ID: {shape.id}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)


    def _draw_shape_path(self, shape: Shape, trajectory_image: np.ndarray) -> None:
        """ Draw the path of the shape on the trajectory image. """
        # each segment is part of the history where the shape was detected, separated by more than xyz (10) None values (overlap or edge of screen)
        history_segments = split_history(shape.history)
        bgr_color = (int(shape.color[2]), int(shape.color[1]), int(shape.color[0]))

        for segment in history_segments:
            if len(segment) > 1:
                # Determine the first valid point in the segment
                first_point = None
                for point in segment:
                    if point[-1] is not None:
                        first_point = point[-1]
                        break

                # add ID to the first point of the segment
                if first_point is not None:
                    text_position = (first_point[0] + 5, first_point[1] - 5)  # Slightly offset the text position
                    cv2.putText(trajectory_image, str(shape.id), text_position, 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, bgr_color, 1, cv2.LINE_AA)

                for i in range(1, len(segment)):
                    start_point = segment[i-1][-1]
                    end_point = segment[i][-1]

                    # prevent empty spaces in the line
                    if start_point is None:
                        start_point = self._find_previous_valid_point(segment, i-1)
                    if end_point is None:
                        end_point = self._find_next_valid_point(segment, i)

                    # draw the line if both points are valid
                    if start_point is not None and end_point is not None:
                        cv2.line(trajectory_image, start_point, end_point, bgr_color, 2)

    def _find_previous_valid_point(self, segment: list, index: int) -> tuple | None:
        for i in range(index, -1, -1):
            if segment[i][-1] is not None:
                return segment[i][-1]
        return None

    def _find_next_valid_point(self, segment: list, index: int) -> tuple | None:
        for i in range(index + 1, len(segment)):
            if segment[i][-1] is not None:
                return segment[i][-1]
        return None

   


