from ._baseprocessor import BaseProcessor
from typing import Any, Dict, Optional, Tuple, cast
from opentelemetry import trace


class SignalProcessor(BaseProcessor):
    def __init__(self):
        self._is_open = False
        self._tracer = trace.get_tracer(__name__)

    def process(self, frame: Any, props: Dict[str, Any]) -> Optional[Tuple[Any, Dict[str, Any]]]:
        with self._tracer.start_as_current_span('process'):
            if 'gate' in props:
                state: str = cast(str, props['__gate']).lower()
                if state == 'open':
                    self._is_open = True
                elif state == 'close':
                    self._is_open = False
            if self._is_open:
                return frame, props
            else:
                return None
