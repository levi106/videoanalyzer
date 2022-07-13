from typing import Any, List, Tuple

from ._node import Node


class TreeBuilder:
    def __init__(self, name: str, data: Any):
        self._root = Node(name, data, [])
        self._tmp_nodes: List[Tuple[str, Node]] = []

    def append(self, name: str, parent: str, data: Any) -> None:
        node = Node(name, data, [])
        parent_node = self._root.find_node(parent)
        if parent_node is not None:
            parent_node.add_child(node)
            for tmp in self._tmp_nodes[:]:
                if tmp[0] == name:
                    node.add_child(tmp[1])
                    self._tmp_nodes.remove(tmp)
        else:
            found = False
            for _, tmp_node in self._tmp_nodes:
                parent_node = tmp_node.find_node(parent)
                if parent_node is not None:
                    parent_node.add_child(node)
                    found = True
                    break
            if not found:
                self._tmp_nodes.append((parent, node))

    @property
    def root(self) -> Node:
        return self._root
