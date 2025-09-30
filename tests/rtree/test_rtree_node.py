"""Unit tests for RTreeNode class."""

from rtree.rectangle import Rectangle
from rtree.rtree_node import RTreeNode


class TestRTreeNode:
    """Test cases for RTreeNode class."""

    def test_node_creation(self) -> None:
        """Test creating an R-tree node."""
        node = RTreeNode(is_leaf=True, max_entries=4)
        assert node.is_leaf is True
        assert node.max_entries == 4
        assert node.min_entries == 2
        assert len(node.entries) == 0
        assert node.parent is None

    def test_mbr_calculation_empty(self) -> None:
        """Test MBR for empty node."""
        node = RTreeNode()
        assert node.mbr is None

    def test_mbr_calculation_single_entry(self) -> None:
        """Test MBR calculation with single entry."""
        node = RTreeNode()
        rect = Rectangle(1.0, 2.0, 3.0, 4.0)
        node.add_entry(rect, "data1")

        mbr = node.mbr
        assert mbr is not None
        assert mbr.x_min == 1.0
        assert mbr.y_min == 2.0
        assert mbr.x_max == 3.0
        assert mbr.y_max == 4.0

    def test_mbr_calculation_multiple_entries(self) -> None:
        """Test MBR calculation with multiple entries."""
        node = RTreeNode()
        node.add_entry(Rectangle(1.0, 1.0, 2.0, 2.0), "data1")
        node.add_entry(Rectangle(3.0, 3.0, 4.0, 4.0), "data2")
        node.add_entry(Rectangle(0.0, 2.0, 1.0, 5.0), "data3")

        mbr = node.mbr
        assert mbr is not None
        assert mbr.x_min == 0.0
        assert mbr.y_min == 1.0
        assert mbr.x_max == 4.0
        assert mbr.y_max == 5.0

    def test_is_full(self) -> None:
        """Test node full status."""
        node = RTreeNode(max_entries=3)
        assert node.is_full() is False

        node.add_entry(Rectangle(1.0, 1.0, 1.0, 1.0), "data1")
        assert node.is_full() is False

        node.add_entry(Rectangle(2.0, 2.0, 2.0, 2.0), "data2")
        assert node.is_full() is False

        node.add_entry(Rectangle(3.0, 3.0, 3.0, 3.0), "data3")
        assert node.is_full() is False  # Still not full at max_entries

        node.add_entry(Rectangle(4.0, 4.0, 4.0, 4.0), "data4")
        assert node.is_full() is True  # Full when exceeding max_entries

    def test_choose_subtree_leaf(self) -> None:
        """Test choose_subtree for leaf node."""
        leaf = RTreeNode(is_leaf=True)
        new_rect = Rectangle(1.0, 1.0, 2.0, 2.0)

        # Leaf should return itself
        chosen = leaf.choose_subtree(new_rect)
        assert chosen == leaf

    def test_choose_subtree_internal(self) -> None:
        """Test choose_subtree for internal node."""
        # Create internal node with child nodes
        internal = RTreeNode(is_leaf=False)

        # Create child nodes with different MBRs
        child1 = RTreeNode(is_leaf=True)
        child1.add_entry(Rectangle(0.0, 0.0, 2.0, 2.0), "data1")

        child2 = RTreeNode(is_leaf=True)
        child2.add_entry(Rectangle(10.0, 10.0, 12.0, 12.0), "data2")

        internal.add_entry(child1.mbr, child1)
        internal.add_entry(child2.mbr, child2)

        # Test choosing subtree for a point near child1
        new_rect = Rectangle(1.0, 1.0, 1.0, 1.0)
        chosen = internal.choose_subtree(new_rect)
        assert chosen == child1  # Should choose child1 (less enlargement)

        # Test choosing subtree for a point near child2
        new_rect2 = Rectangle(11.0, 11.0, 11.0, 11.0)
        chosen2 = internal.choose_subtree(new_rect2)
        assert chosen2 == child2  # Should choose child2 (less enlargement)

    def test_add_entry(self) -> None:
        """Test adding entries to a node."""
        node = RTreeNode()
        rect1 = Rectangle(1.0, 1.0, 2.0, 2.0)
        rect2 = Rectangle(3.0, 3.0, 4.0, 4.0)

        node.add_entry(rect1, "data1")
        assert len(node.entries) == 1
        assert node.entries[0] == (rect1, "data1")

        node.add_entry(rect2, "data2")
        assert len(node.entries) == 2
        assert node.entries[1] == (rect2, "data2")

    def test_quadratic_split_basic(self) -> None:
        """Test quadratic split algorithm."""
        node = RTreeNode(is_leaf=True, max_entries=4)

        # Add entries that should split into two groups
        node.add_entry(Rectangle(1.0, 1.0, 2.0, 2.0), "A")  # Group 1
        node.add_entry(Rectangle(2.0, 2.0, 3.0, 3.0), "B")  # Group 1
        node.add_entry(Rectangle(10.0, 10.0, 11.0, 11.0), "C")  # Group 2
        node.add_entry(Rectangle(11.0, 11.0, 12.0, 12.0), "D")  # Group 2
        node.add_entry(Rectangle(12.0, 12.0, 13.0, 13.0), "E")  # Group 2 (overflow)

        node1, node2 = node.quadratic_split()

        # Check that entries are distributed
        assert len(node1.entries) >= node1.min_entries
        assert len(node2.entries) >= node2.min_entries
        assert len(node1.entries) + len(node2.entries) == 5

        # Check that both nodes are leaves
        assert node1.is_leaf is True
        assert node2.is_leaf is True

    def test_quadratic_split_maintains_minimum(self) -> None:
        """Test that split maintains minimum entries."""
        node = RTreeNode(is_leaf=True, max_entries=6)  # min_entries = 3

        # Add 7 entries to force a split
        for i in range(7):
            node.add_entry(
                Rectangle(float(i), float(i), float(i + 1), float(i + 1)),
                f"data{i}",
            )

        node1, node2 = node.quadratic_split()

        # Both nodes should have at least min_entries
        assert len(node1.entries) >= 3
        assert len(node2.entries) >= 3
        assert len(node1.entries) + len(node2.entries) == 7

    def test_update_mbr_upward(self) -> None:
        """Test MBR update propagation."""
        # Create a simple tree structure
        root = RTreeNode(is_leaf=False)
        child = RTreeNode(is_leaf=True)
        child.parent = root

        # Add child to root
        child_rect = Rectangle(1.0, 1.0, 2.0, 2.0)
        child.add_entry(child_rect, "data")
        root.add_entry(child.mbr, child)

        # Modify child and update MBR
        new_rect = Rectangle(3.0, 3.0, 4.0, 4.0)
        child.add_entry(new_rect, "data2")
        child.update_mbr_upward()

        # Check that root's entry was updated
        assert root.entries[0][0].x_max == 4.0
        assert root.entries[0][0].y_max == 4.0

    def test_search_leaf_node(self) -> None:
        """Test searching in a leaf node."""
        leaf = RTreeNode(is_leaf=True)
        leaf.add_entry(Rectangle(1.0, 1.0, 2.0, 2.0), "data1")
        leaf.add_entry(Rectangle(3.0, 3.0, 4.0, 4.0), "data2")
        leaf.add_entry(Rectangle(5.0, 5.0, 6.0, 6.0), "data3")

        # Search for overlapping rectangle
        query = Rectangle(1.5, 1.5, 3.5, 3.5)
        results = leaf.search(query)
        assert len(results) == 2
        assert "data1" in results
        assert "data2" in results

        # Search for non-overlapping rectangle
        query2 = Rectangle(10.0, 10.0, 11.0, 11.0)
        results2 = leaf.search(query2)
        assert len(results2) == 0

    def test_search_internal_node(self) -> None:
        """Test searching through internal nodes."""
        # Create internal node with children
        internal = RTreeNode(is_leaf=False)

        # Create first child with entries
        child1 = RTreeNode(is_leaf=True)
        child1.add_entry(Rectangle(0.0, 0.0, 2.0, 2.0), "data1")
        child1.add_entry(Rectangle(1.0, 1.0, 3.0, 3.0), "data2")

        # Create second child with entries
        child2 = RTreeNode(is_leaf=True)
        child2.add_entry(Rectangle(10.0, 10.0, 12.0, 12.0), "data3")
        child2.add_entry(Rectangle(11.0, 11.0, 13.0, 13.0), "data4")

        internal.add_entry(child1.mbr, child1)
        internal.add_entry(child2.mbr, child2)

        # Search that hits first child
        query1 = Rectangle(1.5, 1.5, 2.5, 2.5)
        results1 = internal.search(query1)
        assert len(results1) == 2
        assert "data1" in results1
        assert "data2" in results1

        # Search that hits second child
        query2 = Rectangle(11.5, 11.5, 12.5, 12.5)
        results2 = internal.search(query2)
        assert len(results2) == 2
        assert "data3" in results2
        assert "data4" in results2

        # Search that hits nothing
        query3 = Rectangle(5.0, 5.0, 6.0, 6.0)
        results3 = internal.search(query3)
        assert len(results3) == 0

    def test_parent_pointer_maintenance(self) -> None:
        """Test parent pointer maintenance during split."""
        child = RTreeNode(is_leaf=False, max_entries=4)

        # Create grandchildren
        for i in range(5):
            grandchild = RTreeNode(is_leaf=True)
            grandchild.parent = child
            child.add_entry(
                Rectangle(float(i), float(i), float(i + 1), float(i + 1)),
                grandchild,
            )

        child1, child2 = child.quadratic_split()

        # Check parent pointers are maintained
        for _, gc in child1.entries:
            if not child1.is_leaf:
                assert gc.parent == child1

        for _, gc in child2.entries:
            if not child2.is_leaf:
                assert gc.parent == child2

    def test_str_representation(self) -> None:
        """Test string representation of node."""
        node = RTreeNode(is_leaf=True)
        node.add_entry(Rectangle(1.0, 1.0, 2.0, 2.0), "data1")

        str_repr = str(node)
        assert "Leaf" in str_repr
        assert "[(1,1)-(2,2)]" in str_repr
        assert "data1" in str_repr
