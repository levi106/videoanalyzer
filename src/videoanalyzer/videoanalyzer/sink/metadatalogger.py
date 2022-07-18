import json
import logging
from typing import Any, Dict

from opentelemetry import trace

from ._basesink import BaseSink


logger = logging.getLogger(__name__)


class MetadataLogger(BaseSink):
    def __init__(self):
        self._tracer = trace.get_tracer(__name__)

    def write(self, frame: Any, props: Dict[str, Any]) -> None:
        with self._tracer.start_as_current_span('write'):
            logger.info(json.dumps(props))
