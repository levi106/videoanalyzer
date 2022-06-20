from typing import Any, Dict, Tuple
from ._basesource import BaseSource
from opentelemetry import trace

import cv2

class OpenCvSource(BaseSource):
    def __init__(self):
        self._cap: Any = None
        self._tracer = trace.get_tracer(__name__)

    def _create_device(self) -> Any:
        pass

    def read(self) -> Tuple[Any, Dict[str, Any]]:
        with self._tracer.start_as_current_span('read'):
            if self._cap == None:
                self._cap = self._create_device()
                self._width = self._cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                self._height = self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                self._fps = self._cap.get(cv2.CAP_PROP_FPS)

            if not self._cap.isOpened():
                pass

            ret, frame = self._cap.read()
            if ret:
                pos_msec = self._cap.get(cv2.CAP_PROP_POS_MSEC)
                pos_frames = self._cap.get(cv2.CAP_PROP_POS_FRAMES)
            else:
                pos_msec = -1
                pos_frames = -1
            props = {
                'pos_msec': pos_msec,
                'pos_frames': pos_frames,
                'fps': self._fps,
                'width': int(self._width),
                'height': int(self._height)
            }
            return frame, props

    def reset(self) -> None:
        if self._cap != None:
            self._cap.release()
            self._cap = None

