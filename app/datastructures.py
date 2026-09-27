from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

T = TypeVar('T')

@dataclass
class Node(Generic[T]):
    value: T
    next: Optional['Node[T]'] = None

class Stack(Generic[T]):
    """LIFO stack implemented with linked nodes."""
    def __init__(self):
        self.top: Optional[Node[T]] = None
        self._size = 0

    def push(self, value: T) -> None:
        self.top = Node(value, self.top)
        self._size += 1

    def pop(self) -> T:
        if self.top is None:
            raise IndexError('Cannot pop from an empty stack')
        value = self.top.value
        self.top = self.top.next
        self._size -= 1
        return value

    def peek(self) -> T:
        if self.top is None:
            raise IndexError('Cannot peek at an empty stack')
        return self.top.value

    def is_empty(self) -> bool:
        return self.top is None

    def size(self) -> int:
        return self._size

class Queue(Generic[T]):
    """FIFO queue implemented with linked nodes."""
    def __init__(self):
        self.front: Optional[Node[T]] = None
        self.rear: Optional[Node[T]] = None
        self._size = 0

    def enqueue(self, value: T) -> None:
        node = Node(value)
        if self.rear is None:
            self.front = self.rear = node
        else:
            self.rear.next = node
            self.rear = node
        self._size += 1

    def dequeue(self) -> T:
        if self.front is None:
            raise IndexError('Cannot dequeue from an empty queue')
        value = self.front.value
        self.front = self.front.next
        self._size -= 1
        if self.front is None:
            self.rear = None
        return value

    def peek(self) -> T:
        if self.front is None:
            raise IndexError('Cannot peek at an empty queue')
        return self.front.value

    def is_empty(self) -> bool:
        return self.front is None

    def size(self) -> int:
        return self._size
