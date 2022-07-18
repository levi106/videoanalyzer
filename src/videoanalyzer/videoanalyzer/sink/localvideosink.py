import datetime
import logging
import os
from typing import Any, Dict

import cv2

from opentelemetry import trace

from ._basesink import BaseSink


logger = logging.getLogger(__name__)


class LocalVideoSink(BaseSink):
    def __init__(self, output_dir: str, ext: str = 'mp4', fourcc: str = 'mp4v'):
        self._output_dir = output_dir
        self._ext = ext
        self._writer: Any = None
        self._fourcc = cv2.VideoWriter_fourcc(*fourcc)
        self._tracer = trace.get_tracer(__name__)

    def write(self, frame: Any, props: Dict[str, Any]) -> None:
        with self._tracer.start_as_current_span('write'):
            if self._writer is None:
                now = datetime.datetime.now()
                filename = os.path.join(
                    self._output_dir, now.strftime(f'%Y%m%d%H%M%S.{self._ext}'))
                width = props['width']
                height = props['height']
                fps = props['fps']
                logger.info(f'create video writer: path={filename}, fps={fps}, width={width}, height={height}, fourcc={self._fourcc}')
                self._writer = cv2.VideoWriter(
                    filename=filename, fourcc=self._fourcc, fps=fps, frameSize=(width, height))
            self._writer.write(frame)

    def reset(self) -> None:
        self._writer.release()
