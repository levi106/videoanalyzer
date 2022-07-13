import json
from typing import Any, Dict

from azure.iot.device import IoTHubModuleClient

from opentelemetry import trace

from ._basesink import BaseSink


class IoTHubMessageSink(BaseSink):
    def __init__(self, client: IoTHubModuleClient, output_name: str):
        self._tracer = trace.get_tracer(__name__)
        self._client = client
        self._output_name = output_name

    def write(self, frame: Any, props: Dict[str, Any]) -> None:
        self._client.send_message_to_output(
            json.dumps(props), self._output_name)
