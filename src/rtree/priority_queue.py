"""Priority queue implementation for KNN queries."""

import heapq
from typing import Generic, TypeVar

T = TypeVar("T")


class PriorityQueue(Generic[T]):
    """Min-heap based priority queue for efficient KNN queries."""

    def __init__(self) -> None:
        """Initialize an empty priority queue."""
        self._heap: list[tuple[float, int, T]] = []
        self._counter = 0

    def push(self, priority: float, item: T) -> None:
        """
        Push an item onto the queue with a given priority.

        :param priority: Priority value (lower values have higher priority).
        :param item: Item to add to the queue.
        """
        heapq.heappush(self._heap, (priority, self._counter, item))
        self._counter += 1

    def pop(self) -> tuple[float, T]:
        """
        Pop and return the item with lowest priority.

        :return: Tuple of (priority, item).
        :raises IndexError: If the queue is empty.
        """
        if not self._heap:
            raise IndexError("pop from empty priority queue")
        priority, _, item = heapq.heappop(self._heap)
        return priority, item

    def peek(self) -> tuple[float, T]:
        """
        Return the item with lowest priority without removing it.

        :return: Tuple of (priority, item).
        :raises IndexError: If the queue is empty.
        """
        if not self._heap:
            raise IndexError("peek from empty priority queue")
        priority, _, item = self._heap[0]
        return priority, item

    def is_empty(self) -> bool:
        """
        Check if the queue is empty.

        :return: True if queue is empty, False otherwise.
        """
        return len(self._heap) == 0

    def __len__(self) -> int:
        """
        Return the number of items in the queue.

        :return: Number of items in the queue.
        """
        return len(self._heap)
