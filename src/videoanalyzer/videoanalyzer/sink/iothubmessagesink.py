import json
import logging
from typing import Any, Dict

from azure.iot.device import IoTHubModuleClient

from opentelemetry import trace

from ._basesink import BaseSink


logger = logging.getLogger(__name__)


class IoTHubMessageSink(BaseSink):
    def __init__(self, output_name: str):
        self._tracer = trace.get_tracer(__name__)
        self._client = None
        self._output_name = output_name

    @property
    def client(self) -> IoTHubModuleClient:
        return self._client

    @client.setter
    def client(self, client: IoTHubModuleClient) -> None:
        logger.info('set client')
        self._client = client

    def write(self, frame: Any, props: Dict[str, Any]) -> None:
        if self._client is None:
            logger.error('IoTHubModuleClient is None')
            return

        try:
            self._client.send_message_to_output(
                json.dumps(props), self._output_name)
        except Exception as e:
            logger.exception(e)
