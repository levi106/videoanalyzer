from typing import Any
from .opencvsource import OpenCvSource

import cv2

class RtspSource(OpenCvSource):
    def __init__(self, url: str):
        super().__init__()
        self._url = url

    @property
    def url(self) -> str:
        return self._url

    def _create_device(self) -> Any:
        return cv2.VideoCapture(self._url)
