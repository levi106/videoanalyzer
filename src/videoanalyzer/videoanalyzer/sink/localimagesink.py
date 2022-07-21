from typing import Any, Dict

import cv2

from opentelemetry import trace

from ._basesink import BaseSink


class LocalImageSink(BaseSink):
    def __init__(self, output_dir: str, max_samples_per_sec: int = -1):
        self._output_dir = output_dir
        self._max_samples_per_sec = max_samples_per_sec
        self._tm = cv2.TickMeter()
        self._tm.start()
        self._tracer = trace.get_tracer(__name__)

    def write(self, frame: Any, props: Dict[str, Any]) -> None:
        self._tm.stop()
        diff = self._tm.getTimeSec()
        if diff * self._max_samples_per_sec > 1:
            self._tm.reset()
            self._tm.start()
            with self._tracer.start_as_current_span('write'):
                for key in props:
                    print(f'{key}: {props[key]}')
        else:
            self._tm.start()

    def reset(self) -> None:
        self._start = 0
