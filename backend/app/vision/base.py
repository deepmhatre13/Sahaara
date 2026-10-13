from abc import ABC, abstractmethod


class MotionProvider(ABC):
    """Returns whether motion was detected in the current sampling window."""

    @abstractmethod
    def poll(self) -> bool:
        """Return True if motion is currently detected."""
        raise NotImplementedError