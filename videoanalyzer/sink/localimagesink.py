import time
from ._basesink import BaseSink
from typing import Any, Dict, Tuple

class LocalImageSink(BaseSink):
    def __init__(self,  output_dir: str, max_samples_per_sec: int = -1):
        self._output_dir = output_dir
        self._max_samples_per_sec = max_samples_per_sec
        self._start = 0.
    
    def write(self, frame: Any, props: Dict[str, Any]) -> None:
        self._end = time.time()
        diff = self._end - self._start
        if diff * self._max_samples_per_sec > 1:
            for key in props:
                print(f'{key}: {props[key]}')
            self._start = self._end

    def reset(self) -> None:
        self._start = 0