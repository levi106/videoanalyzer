import logging
from typing import Any

import cv2

from .opencvsource import OpenCvSource


logger = logging.getLogger(__name__)


class RtspSource(OpenCvSource):
    def __init__(self, url: str):
        super().__init__()
        self._url = url

    @property
    def url(self) -> str:
        return self._url

    def _create_device(self) -> Any:
        logger.info(f'_create_device: url={self._url}')
        return cv2.VideoCapture(self._url)
