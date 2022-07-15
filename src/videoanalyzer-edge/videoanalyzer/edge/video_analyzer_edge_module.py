import asyncio
import logging
import threading
from typing import Optional, cast
from azure.iot.device import MethodRequest, MethodResponse
from azure.iot.device.aio import IoTHubModuleClient
from videoanalyzer.pipeline import Pipeline, State

logger = logging.getLogger(__name__)


class VideoAnalyzerEdgeModule():
    METHOD_NAME_ACTIVATE = "activate"
    METHOD_NAME_DEACTIVATE = "deactivate"
    METHOD_NAME_SETPIPELINE = "setPipeline"
    METHOD_NAME_DELETEPIPELINE = "deletePipeline"

    def __init__(self):
        self._client = self.create_client()
        self._stop_event = threading.Event()
        self._pipeline: Optional[Pipeline] = None
        pass

    def create_client(self) -> IoTHubModuleClient:
        logger.info('create_client')
        client = cast(IoTHubModuleClient, IoTHubModuleClient.create_from_edge_environment())

        async def __message_handler(message) -> None:
            await self._message_handler(message)

        async def __method_handler(method_request) -> None:
            await self._method_handler(method_request)

        async def __twin_patch_handler(twin_patch) -> None:
            await self._twin_patch_handler(twin_patch)

        try:
            client.on_message_received = __message_handler
            client.on_method_request_received = __method_handler
            client.on_twin_desired_properties_patch_received = __twin_patch_handler
        except Exception as e:
            logger.exception('%s', e)
            client.shutdown()
            raise

        return client

    async def run(self) -> None:
        logger.info('run')
        while not self._stop_event.is_set():
            await asyncio.sleep(1000)

    async def _message_handler(self, message) -> None:
        logger.info('message_handler')
        pass

    def _handle_activate(self, method_request: MethodRequest) -> None:
        if self._pipeline is not None:
            if self._pipeline.state is State.Stopped:
                self._pipeline.start()

    def _handle_deactivate(self, method_request: MethodRequest) -> None:
        if self._pipeline is not None:
            if self._pipeline.state is State.Running:
                self._pipeline.stop()

    def _handle_set_pipeline(self, method_request: MethodRequest) -> None:
        jsonData = method_request.payload
        logger.info(f'{jsonData}')
        if self._pipeline is None:
            self._pipeline = Pipeline.create_from_json(jsonData)

    def _handle_delete_pipeline(self, method_request: MethodRequest) -> None:
        if self._pipeline is not None:
            if self._pipeline.state is State.Stopped:
                self._pipeline = None

    async def _method_handler(self, method_request: MethodRequest) -> None:
        logger.info(f'method_handler: {method_request.name}')
        if method_request.name == self.METHOD_NAME_ACTIVATE:
            self._handle_activate(method_request)
        elif method_request.name == self.METHOD_NAME_DEACTIVATE:
            self._handle_deactivate(method_request)
        elif method_request.name == self.METHOD_NAME_SETPIPELINE:
            self._handle_set_pipeline(method_request)
        elif method_request.name == self.METHOD_NAME_DELETEPIPELINE:
            self._handle_delete_pipeline(method_request)
        else:
            method_response = MethodResponse.create_from_method_request(method_request, 400, None)
            await self._client.send_method_response(method_response)
            return
        method_response = MethodResponse.create_from_method_request(method_request, 200, None)
        await self._client.send_method_response(method_response)

    async def _twin_patch_handler(self, twin_patch) -> None:
        logger.info('twin_patch_handler')

    def terminate(self) -> None:
        logger.info('terminate')
        self._stop_event.set()

    async def shutdown(self) -> None:
        logger.info('shutdown')
        await self._client.shutdown()
