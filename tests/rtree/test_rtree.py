"""Unit tests for RTree class."""

from rtree.rtree import RTree
from rtree.rtree_node import RTreeNode


class TestRTree:
    """Test cases for RTree class."""

    def test_tree_creation(self) -> None:
        """Test creating an R-tree."""
        tree = RTree(max_entries=4)
        assert tree.root is None
        assert tree.max_entries == 4
        assert tree.height == 0
        assert tree.verbose is False

        tree_verbose = RTree(max_entries=3, verbose=True)
        assert tree_verbose.verbose is True

    def test_insert_first_point(self) -> None:
        """Test inserting first point into empty tree."""
        tree = RTree(max_entries=4)
        tree.insert(5.0, 5.0, "first_point")

        assert tree.root is not None
        assert tree.height == 1
        assert len(tree.root.entries) == 1
        assert tree.root.is_leaf is True

        # Check the inserted data
        results = tree.search_point(5.0, 5.0)
        assert len(results) == 1
        assert results[0] == "first_point"

    def test_insert_multiple_points_no_split(self) -> None:
        """Test inserting points without causing split."""
        tree = RTree(max_entries=4)

        points = [
            (1.0, 1.0, "point1"),
            (2.0, 2.0, "point2"),
            (3.0, 3.0, "point3"),
        ]

        for x, y, data in points:
            tree.insert(x, y, data)

        assert tree.height == 1
        assert tree.root is not None
        assert len(tree.root.entries) == 3
        assert tree.root.is_leaf is True

    def test_insert_causes_split(self) -> None:
        """Test insertion that causes node split."""
        tree = RTree(max_entries=3)

        # Insert 3 points (fills the node to max_entries)
        tree.insert(1.0, 1.0, "A")
        tree.insert(2.0, 2.0, "B")
        tree.insert(10.0, 10.0, "C")

        old_height = tree.height
        assert tree.height == 1  # Still a single leaf node

        # Fourth insertion causes split (exceeds max_entries)
        tree.insert(11.0, 11.0, "D")

        assert tree.height > old_height
        assert tree.root is not None
        assert tree.root.is_leaf is False
        assert len(tree.root.entries) == 2

    def test_search_point_exact_match(self) -> None:
        """Test searching for exact point."""
        tree = RTree()

        # Insert test data
        tree.insert(1.0, 1.0, "A")
        tree.insert(2.0, 2.0, "B")
        tree.insert(3.0, 3.0, "C")

        # Search for exact points
        results = tree.search_point(2.0, 2.0)
        assert len(results) == 1
        assert results[0] == "B"

        # Search for non-existent point
        results = tree.search_point(5.0, 5.0)
        assert len(results) == 0

    def test_search_rectangle(self) -> None:
        """Test searching with rectangle query."""
        tree = RTree()

        # Insert grid of points
        points = [
            (1.0, 1.0, "A"),
            (2.0, 1.0, "B"),
            (3.0, 1.0, "C"),
            (1.0, 2.0, "D"),
            (2.0, 2.0, "E"),
            (3.0, 2.0, "F"),
            (1.0, 3.0, "G"),
            (2.0, 3.0, "H"),
            (3.0, 3.0, "I"),
        ]

        for x, y, data in points:
            tree.insert(x, y, data)

        # Search for central rectangle
        results = tree.search_rectangle(1.5, 1.5, 2.5, 2.5)
        assert len(results) == 1
        assert "E" in results

        # Search for larger rectangle
        results = tree.search_rectangle(0.5, 0.5, 2.5, 2.5)
        assert len(results) == 4
        assert set(results) == {"A", "B", "D", "E"}

        # Search for rectangle covering all points
        results = tree.search_rectangle(0.0, 0.0, 4.0, 4.0)
        assert len(results) == 9

    def test_search_empty_tree(self) -> None:
        """Test searching in empty tree."""
        tree = RTree()

        results = tree.search_point(1.0, 1.0)
        assert results == []

        results = tree.search_rectangle(0.0, 0.0, 10.0, 10.0)
        assert results == []

    def test_duplicate_points(self) -> None:
        """Test inserting duplicate points."""
        tree = RTree()

        tree.insert(5.0, 5.0, "first")
        tree.insert(5.0, 5.0, "second")
        tree.insert(5.0, 5.0, "third")

        results = tree.search_point(5.0, 5.0)
        assert len(results) == 3
        assert set(results) == {"first", "second", "third"}

    def test_negative_coordinates(self) -> None:
        """Test with negative coordinates."""
        tree = RTree()

        tree.insert(-5.0, -5.0, "negative")
        tree.insert(0.0, 0.0, "origin")
        tree.insert(5.0, 5.0, "positive")

        results = tree.search_rectangle(-10.0, -10.0, 10.0, 10.0)
        assert len(results) == 3

        results = tree.search_point(-5.0, -5.0)
        assert results == ["negative"]

    def test_large_dataset(self) -> None:
        """Test with larger dataset to verify tree growth."""
        tree = RTree(max_entries=4)

        # Insert 100 points in a grid
        for i in range(10):
            for j in range(10):
                tree.insert(float(i), float(j), f"point_{i}_{j}")

        # Tree should have grown in height
        assert tree.height > 1

        # Search for specific region
        results = tree.search_rectangle(4.5, 4.5, 5.5, 5.5)
        assert len(results) == 1
        assert results[0] == "point_5_5"

        # Search for larger region
        results = tree.search_rectangle(0.0, 0.0, 2.0, 2.0)
        assert len(results) == 9  # 3x3 grid

    def test_tree_balance(self) -> None:
        """Test that tree maintains balance property."""
        tree = RTree(max_entries=3)

        # Insert points that will cause multiple splits
        for i in range(20):
            tree.insert(float(i), float(i), f"point_{i}")

        # Verify all leaves are at same level
        def check_leaf_levels(
            node: RTreeNode,
            level: int,
            leaf_levels: set[int],
        ) -> None:
            if node.is_leaf:
                leaf_levels.add(level)
            else:
                for _, child in node.entries:
                    check_leaf_levels(child, level + 1, leaf_levels)

        if tree.root:
            leaf_levels = set()
            check_leaf_levels(tree.root, 0, leaf_levels)
            assert len(leaf_levels) == 1  # All leaves at same level

    def test_handle_overflow_root_split(self) -> None:
        """Test root split handling."""
        tree = RTree(max_entries=2)  # Small max for easier testing

        # Fill root node to max_entries
        tree.insert(1.0, 1.0, "A")
        tree.insert(2.0, 2.0, "B")
        assert tree.height == 1

        # Third insertion causes split (exceeds max_entries)
        tree.insert(10.0, 10.0, "C")

        assert tree.height == 2
        assert tree.root is not None
        assert tree.root.is_leaf is False

    def test_str_representation(self) -> None:
        """Test string representation of tree."""
        tree = RTree(max_entries=4)

        # Empty tree
        str_repr = str(tree)
        assert "RTree" in str_repr
        assert "Empty" in str_repr

        # Tree with data
        tree.insert(1.0, 1.0, "data")
        str_repr = str(tree)
        assert "RTree" in str_repr
        assert "height=1" in str_repr
        assert "data" in str_repr

    def test_data_integrity_after_splits(self) -> None:
        """Test that no data is lost during splits."""
        tree = RTree(max_entries=3)

        inserted_data = []
        for i in range(50):
            data = f"item_{i}"
            inserted_data.append(data)
            tree.insert(float(i % 10), float(i // 10), data)

        # Search for all data
        results = tree.search_rectangle(-1.0, -1.0, 11.0, 11.0)
        assert set(results) == set(inserted_data)

    def test_insert_with_none_data(self) -> None:
        """Test inserting points with None as data."""
        tree = RTree()

        tree.insert(1.0, 1.0)  # Default data=None
        tree.insert(2.0, 2.0, None)
        tree.insert(3.0, 3.0, "actual_data")

        results = tree.search_rectangle(0.0, 0.0, 4.0, 4.0)
        assert len(results) == 3
        assert None in results
        assert "actual_data" in results

    def test_boundary_search(self) -> None:
        """Test search on exact boundaries."""
        tree = RTree()

        tree.insert(1.0, 1.0, "A")
        tree.insert(2.0, 2.0, "B")
        tree.insert(3.0, 3.0, "C")

        # Search with boundary exactly on point
        results = tree.search_rectangle(2.0, 2.0, 2.0, 2.0)
        assert len(results) == 1
        assert results[0] == "B"

        # Search with boundary between points
        results = tree.search_rectangle(1.5, 1.5, 1.5, 1.5)
        assert len(results) == 0
