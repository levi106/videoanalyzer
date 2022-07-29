import json
import logging
import threading
import time
from typing import Optional, cast

from azure.iot.device import MethodRequest, MethodResponse
from azure.iot.device import IoTHubModuleClient
from azure.iot.device.exceptions import ConnectionFailedError

from tenacity import after_log, before_log, retry, retry_if_exception_type, wait_exponential

from videoanalyzer.pipeline import Pipeline, State

from videoanalyzer.processor import IoTHubMessageProcessor

from videoanalyzer.sink import IoTHubMessageSink


logger = logging.getLogger(__name__)


class VideoAnalyzerEdgeModule():
    METHOD_NAME_ACTIVATE = "activate"
    METHOD_NAME_DEACTIVATE = "deactivate"
    METHOD_NAME_SETPIPELINE = "setPipeline"
    METHOD_NAME_DELETEPIPELINE = "deletePipeline"
    METHOD_NAME_UPDATEMETADATA = "updatemetadata"

    def __init__(self):
        self._client = self.create_client()
        self._stop_event = threading.Event()
        self._pipeline: Optional[Pipeline] = None
        pass

    @retry(wait=wait_exponential(multiplier=1, min=3, max=30),
           retry=retry_if_exception_type((ConnectionFailedError)),
           before=before_log(logger, logging.INFO),
           after=after_log(logger, logging.INFO))
    def _connect_with_retry(self, client: IoTHubModuleClient) -> None:
        def __message_handler(message) -> None:
            self._message_handler(message)

        def __method_handler(method_request) -> None:
            self._method_handler(method_request)

        def __twin_patch_handler(twin_patch) -> None:
            self._twin_patch_handler(twin_patch)

        client.on_message_received = __message_handler
        client.on_method_request_received = __method_handler
        client.on_twin_desired_properties_patch_received = __twin_patch_handler

    def create_client(self) -> IoTHubModuleClient:
        logger.info('create_client')
        client = cast(IoTHubModuleClient, IoTHubModuleClient.create_from_edge_environment())

        try:
            self._connect_with_retry(client)
        except Exception as e:
            logger.exception('%s', e)
            client.shutdown()
            raise

        return client

    def run(self) -> None:
        logger.info('run')
        while not self._stop_event.is_set():
            time.sleep(1000)

    def _message_handler(self, message) -> None:
        logger.info('message_handler')
        pass

    def _handle_activate(self, method_request: MethodRequest) -> None:
        if self._pipeline is not None:
            if self._pipeline.state is State.Stopped:
                try:
                    self._pipeline.start()
                except Exception as e:
                    logger.exception('%s', e)
                    raise

    def _handle_deactivate(self, method_request: MethodRequest) -> None:
        if self._pipeline is not None:
            if self._pipeline.state is State.Running:
                try:
                    self._pipeline.stop()
                except Exception as e:
                    logger.exception('%s', e)
                    raise

    def _handle_set_pipeline(self, method_request: MethodRequest) -> None:
        jsonData = json.dumps(method_request.payload)
        logger.info(f'{jsonData}')
        if self._pipeline is None:
            try:
                self._pipeline = Pipeline.create_from_json(jsonData)
                iotHubSinks = self._pipeline.get_sink(IoTHubMessageSink)
                for sink in iotHubSinks:
                    iotHubSink = cast(IoTHubMessageSink, sink)
                    iotHubSink.client = self._client

            except Exception as e:
                logger.exception('%s', e)
                raise

    def _handle_delete_pipeline(self, method_request: MethodRequest) -> None:
        if self._pipeline is not None:
            if self._pipeline.state is State.Stopped:
                self._pipeline = None

    def _handle_update_metadata(self, method_request: MethodRequest) -> None:
        if self._pipeline is not None:
            iotHubProcessors = self._pipelines.get_processor(IoTHubMessageProcessor)
            for processor in iotHubProcessors:
                iotHubProcessor = cast(IoTHubMessageProcessor, processor)
                iotHubProcessor.update_metadata(method_request.payload)

    def _method_handler(self, method_request: MethodRequest) -> None:
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
            self._client.send_method_response(method_response)
            return
        method_response = MethodResponse.create_from_method_request(method_request, 200, None)
        self._client.send_method_response(method_response)

    def _twin_patch_handler(self, twin_patch) -> None:
        logger.info('twin_patch_handler')

    def terminate(self) -> None:
        logger.info('terminate')
        self._stop_event.set()

    def shutdown(self) -> None:
        logger.info('shutdown')
        self._client.shutdown()
