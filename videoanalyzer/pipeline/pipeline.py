import threading

from ..source import BaseSource
from ..sink import BaseSink
from ..processor import BaseProcessor
from ._node import Node
from ._tree_builder import TreeBuilder
from enum import Enum, auto
from typing import Tuple, List, Any, Dict, Sequence

class State(Enum):
    Running = auto()
    Stopped = auto()

class Pipeline:
    def __init__(self, source: Tuple[str,BaseSource], processors: Sequence[Tuple[str,str,BaseProcessor]] = [], sinks: Sequence[Tuple[str,str,BaseSink]] = []):
        self._state = State.Stopped
        self._lock = threading.Lock()
        self._source = source
        self._sinks = sinks
        self._processors = processors
        self._build_tree()
    
    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, args=())
        self._thread.start()

    def stop(self) -> None:
        self._set_state(State.Stopped)
        self._thread.join()
        self._source[1].reset()
        for sink in self._sinks:
            sink[2].reset()

    def _build_tree(self) -> None:
        builder = TreeBuilder(self._source[0], self._source[1])
        for name, parent, processor in self._processors:
            builder.append(name, parent, processor)
        for name, parent, sink in self._sinks:
            builder.append(name, parent, sink)
        self._tree = builder.root

    def _process(self, node: Node, frame: Any, props: Dict[str,Any]):
        processor: BaseProcessor = node.data
        result = processor.process(frame=frame, props=props)
        if result is not None:
            for child in node:
                self._process(child, result[0], result[1])

    def _run(self) -> None:
        self._set_state(State.Running)
        while True:
            if not self._is_running():
                break
            source = self._tree.data
            frame, props = source.read()
            self._process(self._tree[0], frame, props)

    def _is_running(self) -> bool:
        self._lock.acquire()
        is_running = self._state == State.Running
        self._lock.release()
        return is_running

    def _set_state(self, state: State) -> None:
        self._lock.acquire()
        self._state = state
        self._lock.release()

    @property
    def state(self) -> State:
        self._lock.acquire()
        state = self._state
        self._lock.release()
        return state
