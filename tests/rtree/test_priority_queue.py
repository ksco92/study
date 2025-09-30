"""Unit tests for PriorityQueue class."""

import pytest

from rtree.priority_queue import PriorityQueue


class TestPriorityQueue:
    """Test cases for PriorityQueue class."""

    def test_create_empty_queue(self) -> None:
        """Test creating an empty priority queue."""
        queue: PriorityQueue[str] = PriorityQueue()
        assert queue.is_empty() is True
        assert len(queue) == 0

    def test_push_single_item(self) -> None:
        """Test pushing a single item."""
        queue: PriorityQueue[str] = PriorityQueue()
        queue.push(5.0, "item")

        assert queue.is_empty() is False
        assert len(queue) == 1

    def test_push_and_pop(self) -> None:
        """Test push and pop operations."""
        queue: PriorityQueue[str] = PriorityQueue()
        queue.push(5.0, "item1")

        priority, item = queue.pop()
        assert priority == 5.0
        assert item == "item1"
        assert queue.is_empty() is True

    def test_priority_ordering(self) -> None:
        """Test that items are popped in priority order."""
        queue: PriorityQueue[str] = PriorityQueue()

        # Push items in non-sorted order
        queue.push(5.0, "medium")
        queue.push(1.0, "low")
        queue.push(10.0, "high")

        # Should pop in ascending priority order
        priority1, item1 = queue.pop()
        assert priority1 == 1.0
        assert item1 == "low"

        priority2, item2 = queue.pop()
        assert priority2 == 5.0
        assert item2 == "medium"

        priority3, item3 = queue.pop()
        assert priority3 == 10.0
        assert item3 == "high"

    def test_peek(self) -> None:
        """Test peek operation."""
        queue: PriorityQueue[str] = PriorityQueue()
        queue.push(5.0, "item1")
        queue.push(3.0, "item2")

        # Peek should return lowest priority without removing
        priority, item = queue.peek()
        assert priority == 3.0
        assert item == "item2"
        assert len(queue) == 2

        # Verify queue still has both items
        queue.pop()
        assert len(queue) == 1

    def test_pop_from_empty_queue(self) -> None:
        """Test popping from empty queue raises error."""
        queue: PriorityQueue[str] = PriorityQueue()

        with pytest.raises(IndexError, match="pop from empty priority queue"):
            queue.pop()

    def test_peek_from_empty_queue(self) -> None:
        """Test peeking from empty queue raises error."""
        queue: PriorityQueue[str] = PriorityQueue()

        with pytest.raises(IndexError, match="peek from empty priority queue"):
            queue.peek()

    def test_multiple_items_same_priority(self) -> None:
        """Test handling multiple items with same priority."""
        queue: PriorityQueue[str] = PriorityQueue()

        queue.push(5.0, "item1")
        queue.push(5.0, "item2")
        queue.push(5.0, "item3")

        # All should have same priority
        items = []
        while not queue.is_empty():
            priority, item = queue.pop()
            assert priority == 5.0
            items.append(item)

        # All items should be present (order may vary)
        assert set(items) == {"item1", "item2", "item3"}

    def test_length_tracking(self) -> None:
        """Test that length is tracked correctly."""
        queue: PriorityQueue[int] = PriorityQueue()

        assert len(queue) == 0

        queue.push(1.0, 100)
        assert len(queue) == 1

        queue.push(2.0, 200)
        assert len(queue) == 2

        queue.pop()
        assert len(queue) == 1

        queue.pop()
        assert len(queue) == 0

    def test_is_empty(self) -> None:
        """Test is_empty method."""
        queue: PriorityQueue[str] = PriorityQueue()

        assert queue.is_empty() is True

        queue.push(1.0, "item")
        assert queue.is_empty() is False

        queue.pop()
        assert queue.is_empty() is True

    def test_different_data_types(self) -> None:
        """Test priority queue with different data types."""
        # Integer data
        int_queue: PriorityQueue[int] = PriorityQueue()
        int_queue.push(1.0, 42)
        _, value = int_queue.pop()
        assert value == 42

        # Tuple data
        tuple_queue: PriorityQueue[tuple[int, int]] = PriorityQueue()
        tuple_queue.push(1.0, (1, 2))
        _, value2 = tuple_queue.pop()
        assert value2 == (1, 2)

    def test_negative_priorities(self) -> None:
        """Test with negative priorities."""
        queue: PriorityQueue[str] = PriorityQueue()

        queue.push(-5.0, "negative")
        queue.push(0.0, "zero")
        queue.push(5.0, "positive")

        # Should pop in ascending order
        p1, item1 = queue.pop()
        assert p1 == -5.0
        assert item1 == "negative"

        p2, item2 = queue.pop()
        assert p2 == 0.0
        assert item2 == "zero"

        p3, item3 = queue.pop()
        assert p3 == 5.0
        assert item3 == "positive"

    def test_float_priorities(self) -> None:
        """Test with floating point priorities."""
        queue: PriorityQueue[str] = PriorityQueue()

        queue.push(1.5, "a")
        queue.push(1.1, "b")
        queue.push(1.9, "c")

        _, item1 = queue.pop()
        assert item1 == "b"

        _, item2 = queue.pop()
        assert item2 == "a"

        _, item3 = queue.pop()
        assert item3 == "c"

    def test_large_queue(self) -> None:
        """Test with many items."""
        queue: PriorityQueue[int] = PriorityQueue()

        # Insert 100 items with random priorities
        for i in range(100):
            queue.push(float(100 - i), i)

        assert len(queue) == 100

        # Pop all items and verify they come out in sorted order
        prev_priority = float("-inf")
        for _ in range(100):
            priority, _ = queue.pop()
            assert priority >= prev_priority
            prev_priority = priority

    def test_counter_prevents_comparison_issues(self) -> None:
        """Test that counter prevents item comparison for equal priorities."""
        queue: PriorityQueue[str] = PriorityQueue()

        # Push items with same priority in specific order
        queue.push(1.0, "first")
        queue.push(1.0, "second")
        queue.push(1.0, "third")

        # Should maintain insertion order for equal priorities (FIFO)
        _, item1 = queue.pop()
        _, item2 = queue.pop()
        _, item3 = queue.pop()

        # Due to counter, order should be preserved
        assert item1 == "first"
        assert item2 == "second"
        assert item3 == "third"

    def test_none_values(self) -> None:
        """Test with None as data values."""
        queue: PriorityQueue[str | None] = PriorityQueue()

        queue.push(1.0, None)
        queue.push(2.0, "something")

        priority1, item1 = queue.pop()
        assert priority1 == 1.0
        assert item1 is None

        priority2, item2 = queue.pop()
        assert priority2 == 2.0
        assert item2 == "something"

    def test_zero_priority(self) -> None:
        """Test with zero priority."""
        queue: PriorityQueue[str] = PriorityQueue()

        queue.push(0.0, "zero")
        queue.push(1.0, "one")
        queue.push(-1.0, "negative")

        _, item1 = queue.pop()
        assert item1 == "negative"

        _, item2 = queue.pop()
        assert item2 == "zero"

        _, item3 = queue.pop()
        assert item3 == "one"
