import logging
from typing import Any, Dict, Optional, Tuple

from opentelemetry import trace

from ._baseprocessor import BaseProcessor


logger = logging.getLogger(__name__)


class IoTHubMessageProcessor(BaseProcessor):
    def __init__(self):
        self._tracer = trace.get_tracer(__name__)
        self._props: Dict[str, Any] = {}

    def update_metadata(self, payload: Dict[str, Any]) -> None:
        logger.info(f'update_metadata: {payload}')

    def process(self, frame: Any, props: Dict[str, Any]) -> Optional[Tuple[Any, Dict[str, Any]]]:
        return frame, props | self._props
