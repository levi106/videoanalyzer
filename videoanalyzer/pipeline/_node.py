from typing import List, Iterator, TypeVar, Generic

T = TypeVar('T')

class Node(Generic[T]):
    def __init__(self, name: str, data: T, children: List['Node']):
        self._name = name
        self._data = data
        self._children = children

    def iter(self) -> Iterator['Node']:
        for child in self._children:
            yield child

    def __len__(self) -> int:
        return len(self._children)

    def __getitem__(self, ind: int) -> 'Node':
        return self._children[ind]

    @property
    def data(self) -> T:
        return self._data

    @property
    def name(self) -> str:
        return self._name

    def add_child(self, child: 'Node') -> None:
        self._children.append(child)