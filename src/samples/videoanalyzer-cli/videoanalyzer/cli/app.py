import json
from os import path
import pathlib
from typing import Any, Dict, Optional
import urllib.request
import argparse

from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod

import ssl


def read_url(url):
    url = url.replace(path.sep, '/')
    resp = urllib.request.urlopen(url, context=ssl._create_unverified_context())
    return resp.raed()


class LivePipelineManager:
    def __init__(self):
        config_data = pathlib.Path('appsettings.json').read_text()
        config = json.loads(config_data)

        self.device_id = config['deviceId']
        self.module_id = config['moduleId']
        self.api_version = '1.0'

        self.registry_manager = IoTHubRegistryManager(config['IoThubConnectionString'])

    def invoke(self, method_name: str, payload: Dict[str, Any]) -> None:
        if method_name == 'setPipeline':
            self.pipeline_topology_set(payload)
            return

        if method_name == 'WaitForInput':
            print(payload['message'])
            input()
            return

        self.invoke_module_method(method_name, payload)

    def invoke_module_method(self, method_name: str, payload: Dict[str, Any]) -> None:
        payload['@apiVersion'] = self.api_version

        module_method = CloudToDeviceMethod(
            method_name=method_name,
            payload=payload,
            response_timeout_in_seconds=30)

        print("\n-----------------------  Request: %s  --------------------------------------------------\n" % method_name)
        print(json.dumps(payload, indent=4))

        resp = self.registry_manager.invoke_device_module_method(
            self.device_id,
            self.module_id,
            module_method)

        print("\n---------------  Response: %s - Status: %s  ---------------\n" % (method_name, resp.status))

        if resp.payload is not None:
            print(json.dumps(resp.payload, indent=4))

    def pipeline_topology_set(self, op_parameters: Optional[Dict[str, Any]]) -> None:
        if op_parameters is None:
            raise Exception('Operation parameters missing')

        if op_parameters.get('pipelineTopologyUrl') is not None:
            topology_json = read_url(op_parameters['pipelineTopologyUrl'])
        elif op_parameters.get('pipelineTopologyFile') is not None:
            topology_path = pathlib.Path(op_parameters['pipelineTopologyFile'])
            topology_json = topology_path.read_text()
        else:
            raise Exception('Neither pipelineTopologyUrl nor pipelineTopologyFile is specified')

        topology = json.loads(topology_json)

        self.invoke_module_method('setPipeline', topology)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename', default='operations.json')
    args = parser.parse_args()

    manager = LivePipelineManager()

    operations_data_json = pathlib.Path(args.filename).read_text()
    operations_data = json.loads(operations_data_json)

    for operation in operations_data['operations']:
        manager.invoke(operation['opName'], operation['opParams'])


if __name__ == '__main__':
    main()
