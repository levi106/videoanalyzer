import logging
from typing import Any, Dict, Tuple

import cv2

from opentelemetry import trace

from ._basesource import BaseSource


logger = logging.getLogger(__name__)


class OpenCvSource(BaseSource):
    def __init__(self):
        self._cap: Any = None
        self._tracer = trace.get_tracer(__name__)

    def _create_device(self) -> Any:
        pass

    def read(self) -> Tuple[Any, Dict[str, Any]]:
        logger.debug('read')
        with self._tracer.start_as_current_span('read'):
            if self._cap is None:
                self._cap = self._create_device()
                self._width = self._cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                self._height = self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                self._cap_fps = self._cap.get(cv2.CAP_PROP_FPS)
                self._fps = -1
                self._count = 0
                self._tm = cv2.TickMeter()
                self._tm.start()
                logger.info(f'with: {self._width}, height: {self._height}, fps: {self._fps}({self._cap_fps})')

            if not self._cap.isOpened():
                pass

            ret, frame = self._cap.read()
            if ret:
                pos_msec = self._cap.get(cv2.CAP_PROP_POS_MSEC)
                pos_frames = self._cap.get(cv2.CAP_PROP_POS_FRAMES)
            else:
                pos_msec = -1
                pos_frames = -1

            if self._count == 10:
                self._tm.stop()
                self._fps = self._count / self._tm.getTimeSec()
                self._tm.reset()
                self._tm.start()
                self._count = 0

            self._count += 1

            props = {
                'pos_msec': pos_msec,
                'pos_frames': pos_frames,
                'fps': self._fps,
                'cap_fps': self._cap_fps,
                'width': int(self._width),
                'height': int(self._height)
            }
            logger.debug(f'pos_msec={pos_msec}, pos_frames={pos_frames}, fps={self._fps}({self._cap_fps}), width={self._width}, height={self._height}')
            return frame, props

    def reset(self) -> None:
        logger.info('reset')
        if self._cap is not None:
            self._cap.release()
            self._cap = None
