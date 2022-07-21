import datetime
import logging
import os
from typing import Any, Dict

import cv2

from opentelemetry import trace

from ._basesink import BaseSink


logger = logging.getLogger(__name__)


class LocalVideoSink(BaseSink):
    def __init__(self, output_dir: str, ext: str = 'mp4', fourcc: str = 'mp4v', max_samples_per_sec: int = -1):
        self._output_dir = output_dir
        self._ext = ext
        self._writer: Any = None
        self._fourcc = cv2.VideoWriter_fourcc(*fourcc)
        self._max_samples_per_sec = max_samples_per_sec
        self._tm = cv2.TickMeter()
        if self._max_samples_per_sec > 0:
            self._tm.start()
        self._tracer = trace.get_tracer(__name__)

    def _write(self, frame: Any, props: Dict[str, Any], fps: Any) -> None:
        with self._tracer.start_as_current_span('write'):
            if self._writer is None:
                now = datetime.datetime.now()
                filename = os.path.join(
                    self._output_dir, now.strftime(f'%Y%m%d%H%M%S.{self._ext}'))
                width = props['width']
                height = props['height']
                logger.info(f'create video writer: path={filename}, fps={fps}, width={width}, height={height}, fourcc={self._fourcc}')
                self._writer = cv2.VideoWriter(
                    filename=filename, fourcc=self._fourcc, fps=fps, frameSize=(width, height))
            self._writer.write(frame)

    def write(self, frame: Any, props: Dict[str, Any]) -> None:
        if self._max_samples_per_sec > 0:
            self._tm.stop()
            diff = self._tm.getTimeSec()
            if diff * self._max_samples_per_sec > 1:
                self._tm.reset()
                self._tm.start()
                self._write(frame, props, self._max_samples_per_sec)
        else:
            fps = props['fps']
            cap_fps = props['cap_fps']
            if cap_fps > 0 and cap_fps < 100:
                fps = cap_fps
            if fps > 0:
                self._write(frame, props, fps)

    def reset(self) -> None:
        if self._write is not None:
            self._writer.release()
