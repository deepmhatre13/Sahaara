import random

from app.vision.base import MotionProvider


class MockMotionProvider(MotionProvider):
    """Headless-safe simulator. No camera required — biases toward motion
    so local development doesn't constantly trip inactivity alerts."""

    def __init__(self, motion_probability: float = 0.85) -> None:
        self.motion_probability = motion_probability

    def poll(self) -> bool:
        return random.random() < self.motion_probability