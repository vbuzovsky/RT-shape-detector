import cv2
import numpy as np

class Detector:
    """ 
        simple class that manages the detection of shapes in given image (frame). 

        Methods
        -------
        detect_circles(frame: np.array) -> list

        detect_rectangles(frame: np.array) -> list
    """

    def detect_circles(self, frame: np.ndarray) -> list:
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # needed for HoughCircles

        # simple preprocessing for better circle detection
        _, thresholded_image = cv2.threshold(gray_image, 11, 255, cv2.THRESH_BINARY)
        blurred_image = cv2.blur(thresholded_image, (4, 4))

        circles = cv2.HoughCircles(
            blurred_image,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=20,
            param1=50,
            param2=30,
            minRadius=10,
            maxRadius=0
        )

        # convert np.int64 values to int
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            circles = [(int(x), int(y), int(z)) for (x, y, z) in circles] 

        return circles

    def detect_rectangles(self, frame: np.ndarray) -> list:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        blurred = cv2.medianBlur(gray, 5)
        edged = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        rectangles = []
        for contour in contours:
            approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
            if len(approx) == 4:
                (x, y, w, h) = cv2.boundingRect(approx)
                rectangles.append((x, y, x + w, y + h))

        return rectangles