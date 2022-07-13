import asyncio
import logging
import threading
from typing import cast
from azure.iot.device import MethodRequest, MethodResponse
from azure.iot.device.aio import IoTHubModuleClient

logger = logging.getLogger(__name__)


class VideoAnalyzerEdgeModule():
    METHOD_NAME_ACTIVATE = "activate"
    METHOD_NAME_DEACTIVATE = "deactivate"
    METHOD_NAME_SETPIPELINE = "setPipeline"
    METHOD_NAME_DELETEPIPELINE = "deletePipeline"

    def __init__(self):
        self._client = self.create_client()
        self._stop_event = threading.Event()
        pass

    def create_client(self) -> IoTHubModuleClient:
        client = cast(IoTHubModuleClient, IoTHubModuleClient.create_from_edge_environment())

        async def _message_handler(message) -> None:
            await self.message_handler(message)

        async def _method_handler(method_request) -> None:
            await self.method_handler(method_request)

        async def _twin_patch_handler(twin_patch) -> None:
            await self.twin_patch_handler(twin_patch)

        try:
            client.on_message_received = _message_handler
            client.on_method_request_received = _method_handler
            client.on_twin_desired_properties_patch_received = _twin_patch_handler
        except Exception as e:
            logger.exception('%s', e)
            client.shutdown()
            raise

        return client

    async def run(self) -> None:
        while not self._stop_event.is_set():
            await asyncio.sleep(1000)

    async def message_handler(self, message) -> None:
        logger.debug('message_handler')
        pass

    async def method_handler(self, method_request: MethodRequest) -> None:
        logger.debug(f'method_handler: {method_request.name}')
        if method_request.name == self.METHOD_NAME_ACTIVATE:
            pass
        elif method_request.name == self.METHOD_NAME_DEACTIVATE:
            pass
        elif method_request.name == self.METHOD_NAME_SETPIPELINE:
            pass
        elif method_request.name == self.METHOD_NAME_DELETEPIPELINE:
            pass
        else:
            method_response = MethodResponse.create_from_method_request(method_request, 400, None)
            await self._client.send_method_response(method_response)
            return
        method_response = MethodResponse.create_from_method_request(method_request, 200, None)
        await self._client.send_method_response(method_response)

    async def twin_patch_handler(self, twin_patch) -> None:
        logger.debug('twin_patch_handler')
        pass

    def terminate(self) -> None:
        self._stop_event.set()

    async def shutdown(self) -> None:
        await self._client.shutdown()
