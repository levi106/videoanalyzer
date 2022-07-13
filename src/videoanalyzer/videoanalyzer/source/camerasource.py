from typing import Any

import cv2

from .opencvsource import OpenCvSource


class CameraSource(OpenCvSource):
    def __init__(self, camera_index: int = 0):
        super().__init__()
        self._camera_index = camera_index

    @property
    def camera_index(self) -> int:
        return self._camera_index

    def _create_device(self) -> Any:
        return cv2.VideoCapture(self._camera_index)
