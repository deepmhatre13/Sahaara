import logging

import cv2
import numpy as np

from app.vision.base import MotionProvider

logger = logging.getLogger(__name__)


class OpenCVMotionProvider(MotionProvider):
    """Real-camera frame-diff motion detector. Headless — no cv2.imshow.
    Falls back gracefully (poll() returns False) if the camera is unavailable."""

    def __init__(self, camera_index: int = 0, min_contour_area: int = 1000) -> None:
        self.min_contour_area = min_contour_area
        self._cap = cv2.VideoCapture(camera_index)
        self._prev_frame: np.ndarray | None = None
        if not self._cap.isOpened():
            logger.warning("Camera at index %s could not be opened; motion provider disabled", camera_index)

    def poll(self) -> bool:
        if not self._cap.isOpened():
            return False

        ret, frame = self._cap.read()
        if not ret:
            return False

        if self._prev_frame is None:
            self._prev_frame = frame
            return False

        diff = cv2.absdiff(self._prev_frame, frame)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=3)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        self._prev_frame = frame
        return any(cv2.contourArea(c) > self.min_contour_area for c in contours)

    def __del__(self):
        if self._cap is not None and self._cap.isOpened():
            self._cap.release()