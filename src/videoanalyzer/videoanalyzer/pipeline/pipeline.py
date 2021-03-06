import json
import logging
import threading
from enum import Enum, auto
from importlib import import_module
from typing import Any, Dict, List, Sequence, Tuple, Type

from opentelemetry import trace

from ._node import Node
from ._treebuilder import TreeBuilder
from ..processor import BaseProcessor
from ..sink import BaseSink
from ..source import BaseSource


logger = logging.getLogger(__name__)


class State(Enum):
    Running = auto()
    Stopped = auto()


def _get_class(type: str):
    try:
        module_name, class_name = type.rsplit('.', 1)
        module = import_module(module_name)
        return getattr(module, class_name)
    except (ImportError, AttributeError):
        raise ImportError(type)


class Pipeline:
    API_VERSION = '1.0'
    TOPOLOGY_KEY_NAME = 'name'
    TOPOLOGY_KEY_APIVERSION = '@apiVersion'
    TOPOLOGY_KEY_PROPERTIES = 'properties'
    TOPOLOGY_KEY_SOURCE = 'source'
    TOPOLOGY_KEY_SINKS = 'sinks'
    TOPOLOGY_KEY_PROCESSORS = 'processors'
    TOPOLOGY_KEY_TYPE = '@type'
    TOPOLOGY_KEY_INPUT = 'input'
    TOPOLOGY_KEY_NODENAME = 'nodeName'
    TOPOLOGY_KEY_PARAMETERS = 'parameters'

    def __init__(self, source: Tuple[str, BaseSource], processors: Sequence[Tuple[str, str, BaseProcessor]] = [], sinks: Sequence[Tuple[str, str, BaseSink]] = [], name: str = ""):
        self._tracer = trace.get_tracer(__name__)
        self._state = State.Stopped
        self._lock = threading.Lock()
        self._source = source
        self._sinks = sinks
        self._processors = processors
        self._name = name
        self._build_tree()

    def start(self) -> None:
        logger.info('start')
        self._thread = threading.Thread(target=self._run, args=())
        self._thread.daemon = True
        self._thread.start()

    def stop(self) -> None:
        logger.info('stop')
        self._set_state(State.Stopped)
        self._thread.join()
        self._source[1].reset()
        for sink in self._sinks:
            sink[2].reset()

    def get_source(self) -> BaseSource:
        return self._source[1]

    def get_processor(self, target_type: Type) -> List[BaseProcessor]:
        result: List[BaseProcessor] = []
        for _, _, processor in self._processors:
            if isinstance(processor, target_type):
                result.append(processor)
        return result

    def get_sink(self, target_type: Type) -> List[BaseSink]:
        result: List[BaseSink] = []
        for _, _, sink in self._sinks:
            if isinstance(sink, target_type):
                result.append(sink)
        return result

    def _build_tree(self) -> None:
        logger.info('build_tree')
        with self._tracer.start_as_current_span('build_tree'):
            builder = TreeBuilder(self._source[0], self._source[1])
            for name, parent, processor in self._processors:
                builder.append(name, parent, processor)
            for name, parent, sink in self._sinks:
                builder.append(name, parent, sink)
            self._tree = builder.root

    def _process(self, node: Node, frame: Any, props: Dict[str, Any]):
        processor: BaseProcessor = node.data
        result = processor.process(frame=frame, props=props)
        if result is not None:
            for child in node:
                self._process(child, result[0], result[1])

    def _run(self) -> None:
        logger.info('run')
        self._set_state(State.Running)
        while True:
            if not self._is_running():
                break
            source = self._tree.data
            with self._tracer.start_as_current_span('process_frame'):
                frame, props = source.read()
                self._process(self._tree[0], frame, props)
        logger.info('exit run')

    def _is_running(self) -> bool:
        self._lock.acquire()
        is_running = self._state == State.Running
        self._lock.release()
        return is_running

    def _set_state(self, state: State) -> None:
        logger.info(f'set_state: {self._state} -> {state}')
        self._lock.acquire()
        self._state = state
        self._lock.release()

    @property
    def state(self) -> State:
        self._lock.acquire()
        state = self._state
        self._lock.release()
        return state

    @classmethod
    def _create_instance(cls, type_info: Dict[str, Any]) -> Any:
        name = type_info[cls.TOPOLOGY_KEY_NAME]
        type_name = type_info[cls.TOPOLOGY_KEY_TYPE]
        constructor = _get_class(type_name)
        params = type_info.get(cls.TOPOLOGY_KEY_PARAMETERS, {})
        logger.info(f'create_instance: {type_name}')
        if cls.TOPOLOGY_KEY_INPUT in type_info:
            upper = type_info[cls.TOPOLOGY_KEY_INPUT][cls.TOPOLOGY_KEY_NODENAME]
            return name, upper, constructor(**params)
        else:
            return name, constructor(**params)

    @classmethod
    def create_from_json(cls, jsonData: str) -> 'Pipeline':
        logger.info(f'create_from_json: {jsonData}')
        topology = json.loads(jsonData)
        name = topology[cls.TOPOLOGY_KEY_NAME]
        apiVersion = topology[cls.TOPOLOGY_KEY_APIVERSION]
        if apiVersion != cls.API_VERSION:
            raise Exception('Invalid API version {}'.format(apiVersion))
        properties = topology[cls.TOPOLOGY_KEY_PROPERTIES]
        source = cls._create_instance(properties[cls.TOPOLOGY_KEY_SOURCE])
        processors = [cls._create_instance(
            processor) for processor in properties[cls.TOPOLOGY_KEY_PROCESSORS]]
        sinks = [cls._create_instance(sink)
                 for sink in properties[cls.TOPOLOGY_KEY_SINKS]]

        return cls(source=source, processors=processors, sinks=sinks, name=name)
