from typing import Any

import cv2

from .opencvsource import OpenCvSource


class RtspSource(OpenCvSource):
    def __init__(self, url: str):
        super().__init__()
        self._url = url

    @property
    def url(self) -> str:
        return self._url

    def _create_device(self) -> Any:
        return cv2.VideoCapture(self._url)
