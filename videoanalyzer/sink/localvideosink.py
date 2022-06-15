from ._basesink import BaseSink
from typing import Any, Dict, Tuple

import cv2
import os
import datetime

class LocalVideoSink(BaseSink):
    def __init__(self,  output_dir: str):
        self._output_dir = output_dir
        self._writer:Any = None
        self._fourcc = cv2.VideoWriter_fourcc(*'X264')
    
    def write(self, frame: Any, props:Dict[str, Any]) -> None:
        if self._writer == None:
            now = datetime.datetime.now()
            filename = os.path.join(self._output_dir, now.strftime('%Y%m%d%H%M%S.mkv'))
            width = props['width']
            height = props['height']
            fps = props['fps']
            self._writer = cv2.VideoWriter(filename=filename, fourcc=self._fourcc, fps=fps, frameSize=(width, height))
        self._writer.write(frame)

    def reset(self) -> None:
        self._writer.release()