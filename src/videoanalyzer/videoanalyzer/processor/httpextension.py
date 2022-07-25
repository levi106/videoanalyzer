import json
import logging
import time
from io import BytesIO
from typing import Any, Dict, Optional, Tuple

import cv2

from opentelemetry import trace

import requests

from ._baseprocessor import BaseProcessor


logger = logging.getLogger(__name__)


class HttpExtension(BaseProcessor):
    def __init__(self, url: str, max_samples_per_sec: int = -1):
        self._tracer = trace.get_tracer(__name__)
        self._url = url
        self._max_samples_per_sec = max_samples_per_sec
        self._start = 0.

    def process(self, frame: Any, props: Dict[str, Any]) -> Optional[Tuple[Any, Dict[str, Any]]]:
        with self._tracer.start_as_current_span('process'):
            self._end = time.time()
            diff = self._end - self._start
            if self._max_samples_per_sec == -1 or diff * self._max_samples_per_sec > 1:
                files = {
                    'file': ('frame.png', BytesIO(cv2.imencode('.png', frame)[1].tobytes()))
                }
                try:
                    r = requests.post(
                        self._url, data={'data': json.dumps(props)}, files=files)
                    props.update(r.json())
                except Exception as e:
                    logger.exception(e)
                self._start = self._end

            return frame, props

    def reset(self) -> None:
        self._start = 0
