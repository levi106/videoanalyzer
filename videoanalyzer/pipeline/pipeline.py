import threading

from ..source import BaseSource
from ..sink import BaseSink
from ._node import Node
from enum import Enum, auto
from typing import Dict, Tuple

class State(Enum):
    Running = auto()
    Stopped = auto()

class Pipeline:
    def __init__(self, source: Tuple[str,BaseSource], sinks: Dict[str,Tuple[str,BaseSink]]):
        self._state = State.Stopped
        self._lock = threading.Lock()
        self._source = source
        self._sinks = sinks
        self._build_tree()
    
    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, args=())
        self._thread.start()

    def stop(self) -> None:
        self._set_state(State.Stopped)
        self._thread.join()
        self._source[1].reset()
        for _,v in self._sinks.items():
            v[1].reset()

    def _build_tree(self) -> None:
        root = Node(self._source[0], self._source[1], [])
        for k,v in self._sinks.items():
            if root.name == v[0]:
                root.add_child(Node(k, v[1], []))
        self._tree = root

    def _run(self) -> None:
        self._set_state(State.Running)
        while True:
            if not self._is_running():
                break
            source = self._tree.data
            frame, props = source.read()
            for sink in iter(self._tree):
                sink.data.write(frame=frame, props=props)

    def _is_running(self) -> bool:
        self._lock.acquire()
        is_running = self._state == State.Running
        self._lock.release()
        return is_running

    def _set_state(self, state: State) -> None:
        self._lock.acquire()
        self._state = state
        self._lock.release()
