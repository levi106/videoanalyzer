import json
from logging import getLogger
from ._basesink import BaseSink
from typing import Any, Dict
from opentelemetry import trace


class MetadataLogger(BaseSink):
    def __init__(self):
        self._tracer = trace.get_tracer(__name__)
        self._logger = getLogger(__name__)

    def write(self, frame: Any, props: Dict[str, Any]) -> None:
        with self._tracer.start_as_current_span('write'):
            self._logger.info(json.dumps(props))
