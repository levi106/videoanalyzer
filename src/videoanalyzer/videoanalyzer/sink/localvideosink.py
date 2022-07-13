import datetime
import os
from typing import Any, Dict

import cv2

from opentelemetry import trace

from ._basesink import BaseSink


class LocalVideoSink(BaseSink):
    def __init__(self, output_dir: str):
        self._output_dir = output_dir
        self._writer: Any = None
        self._fourcc = cv2.VideoWriter_fourcc(*'X264')
        self._tracer = trace.get_tracer(__name__)

    def write(self, frame: Any, props: Dict[str, Any]) -> None:
        with self._tracer.start_as_current_span('write'):
            if self._writer is None:
                now = datetime.datetime.now()
                filename = os.path.join(
                    self._output_dir, now.strftime('%Y%m%d%H%M%S.mkv'))
                width = props['width']
                height = props['height']
                fps = props['fps']
                self._writer = cv2.VideoWriter(
                    filename=filename, fourcc=self._fourcc, fps=fps, frameSize=(width, height))
            self._writer.write(frame)

    def reset(self) -> None:
        self._writer.release()
