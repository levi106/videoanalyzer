import json
from unittest import mock
from videoanalyzer.sink.iothubmessagesink import IoTHubMessageSink
from azure.iot.device import IoTHubModuleClient

@mock.patch('azure.iot.device.IoTHubModuleClient.__new__')
def test_write(mock_iotHubModuleClient):
    instance = mock.MagicMock()
    mock_iotHubModuleClient.return_value = instance
    output_name = "out1"
    props = {'prop1': 'value1', 'prop2': 'value2'}
 
    client = IoTHubModuleClient()
    sink = IoTHubMessageSink(client=client,output_name=output_name)
    sink.write(frame=None,props=props)

    instance.send_message_to_output.assert_called_once_with(json.dumps(props), output_name)