"""Unit tests for KNN (K-Nearest Neighbors) functionality."""

from rtree.rtree import RTree


class TestKNN:
    """Test cases for KNN queries."""

    def test_knn_empty_tree(self) -> None:
        """Test KNN on empty tree."""
        tree = RTree()
        results = tree.knn(5.0, 5.0, 3)
        assert results == []

    def test_knn_single_point(self) -> None:
        """Test KNN with single point."""
        tree = RTree()
        tree.insert(5.0, 5.0, "A")

        results = tree.knn(5.0, 5.0, 1)
        assert len(results) == 1
        assert results[0][0] == "A"
        assert results[0][1] == 0.0

    def test_knn_k_zero(self) -> None:
        """Test KNN with k=0."""
        tree = RTree()
        tree.insert(1.0, 1.0, "A")
        tree.insert(2.0, 2.0, "B")

        results = tree.knn(0.0, 0.0, 0)
        assert results == []

    def test_knn_k_negative(self) -> None:
        """Test KNN with negative k."""
        tree = RTree()
        tree.insert(1.0, 1.0, "A")

        results = tree.knn(0.0, 0.0, -1)
        assert results == []

    def test_knn_basic_ordering(self) -> None:
        """Test KNN returns points in correct distance order."""
        tree = RTree()

        # Insert points at different distances from origin
        tree.insert(1.0, 0.0, "A")  # Distance 1
        tree.insert(2.0, 0.0, "B")  # Distance 2
        tree.insert(3.0, 0.0, "C")  # Distance 3
        tree.insert(4.0, 0.0, "D")  # Distance 4

        results = tree.knn(0.0, 0.0, 3)

        assert len(results) == 3
        assert results[0][0] == "A"
        assert results[1][0] == "B"
        assert results[2][0] == "C"

        # Check distances are in ascending order
        for i in range(len(results) - 1):
            assert results[i][1] <= results[i + 1][1]

    def test_knn_exact_distance_calculation(self) -> None:
        """Test KNN calculates distances correctly."""
        tree = RTree()

        # Insert points at known distances
        tree.insert(3.0, 4.0, "A")  # Distance 5 from origin
        tree.insert(5.0, 12.0, "B")  # Distance 13 from origin
        tree.insert(0.0, 0.0, "C")  # Distance 0 from origin

        results = tree.knn(0.0, 0.0, 3)

        assert len(results) == 3
        assert results[0][0] == "C"
        assert results[0][1] == 0.0
        assert results[1][0] == "A"
        assert abs(results[1][1] - 5.0) < 0.001
        assert results[2][0] == "B"
        assert abs(results[2][1] - 13.0) < 0.001

    def test_knn_k_greater_than_points(self) -> None:
        """Test KNN when k is greater than number of points."""
        tree = RTree()

        tree.insert(1.0, 1.0, "A")
        tree.insert(2.0, 2.0, "B")

        results = tree.knn(0.0, 0.0, 10)

        assert len(results) == 2
        assert results[0][0] == "A"
        assert results[1][0] == "B"

    def test_knn_with_duplicate_distances(self) -> None:
        """Test KNN with points at equal distances."""
        tree = RTree()

        # Points at equal distance from origin (distance 1)
        tree.insert(1.0, 0.0, "A")
        tree.insert(0.0, 1.0, "B")
        tree.insert(-1.0, 0.0, "C")
        tree.insert(0.0, -1.0, "D")

        results = tree.knn(0.0, 0.0, 4)

        assert len(results) == 4
        # All should have distance approximately 1
        for _, dist in results:
            assert abs(dist - 1.0) < 0.001

    def test_knn_query_point_not_at_origin(self) -> None:
        """Test KNN with query point not at origin."""
        tree = RTree()

        tree.insert(5.0, 5.0, "A")
        tree.insert(6.0, 5.0, "B")
        tree.insert(5.0, 6.0, "C")
        tree.insert(10.0, 10.0, "D")

        results = tree.knn(5.0, 5.0, 3)

        assert len(results) == 3
        assert results[0][0] == "A"
        assert results[0][1] == 0.0
        assert results[1][0] in ["B", "C"]
        assert abs(results[1][1] - 1.0) < 0.001
        assert results[2][0] in ["B", "C"]
        assert abs(results[2][1] - 1.0) < 0.001

    def test_knn_negative_coordinates(self) -> None:
        """Test KNN with negative coordinates."""
        tree = RTree()

        tree.insert(-5.0, -5.0, "A")
        tree.insert(-3.0, -3.0, "B")
        tree.insert(-1.0, -1.0, "C")
        tree.insert(1.0, 1.0, "D")

        results = tree.knn(-4.0, -4.0, 2)

        assert len(results) == 2
        assert results[0][0] == "A"
        assert results[1][0] == "B"

    def test_knn_large_dataset(self) -> None:
        """Test KNN with larger dataset."""
        tree = RTree(max_entries=4)

        # Insert 100 points in a grid
        for i in range(10):
            for j in range(10):
                tree.insert(float(i), float(j), f"point_{i}_{j}")

        # Query for 5 nearest neighbors to a central point
        results = tree.knn(5.0, 5.0, 5)

        assert len(results) == 5
        # The nearest should be the point at (5, 5)
        assert results[0][0] == "point_5_5"
        assert results[0][1] == 0.0

        # Check distances are in ascending order
        for i in range(len(results) - 1):
            assert results[i][1] <= results[i + 1][1]

    def test_knn_corner_query(self) -> None:
        """Test KNN with query at corner of point cloud."""
        tree = RTree()

        # Create a 5x5 grid
        for i in range(5):
            for j in range(5):
                tree.insert(float(i), float(j), f"p_{i}_{j}")

        # Query from bottom-left corner
        results = tree.knn(0.0, 0.0, 3)

        assert len(results) == 3
        assert results[0][0] == "p_0_0"
        assert results[0][1] == 0.0

    def test_knn_with_none_data(self) -> None:
        """Test KNN with None as data."""
        tree = RTree()

        tree.insert(1.0, 1.0, None)
        tree.insert(2.0, 2.0, "B")
        tree.insert(3.0, 3.0, None)

        results = tree.knn(0.0, 0.0, 3)

        assert len(results) == 3
        assert results[0][0] is None
        assert results[1][0] == "B"
        assert results[2][0] is None

    def test_knn_distance_ordering_strict(self) -> None:
        """Test that KNN strictly orders by distance."""
        tree = RTree()

        # Insert points in random order
        points = [
            (10.0, 10.0, "far"),
            (1.0, 1.0, "near"),
            (5.0, 5.0, "medium"),
            (0.5, 0.5, "nearest"),
        ]

        for x, y, data in points:
            tree.insert(x, y, data)

        results = tree.knn(0.0, 0.0, 4)

        # Verify strict distance ordering
        assert results[0][0] == "nearest"
        assert results[1][0] == "near"
        assert results[2][0] == "medium"
        assert results[3][0] == "far"

    def test_knn_with_splits(self) -> None:
        """Test KNN works correctly after tree splits."""
        tree = RTree(max_entries=3)

        # Insert enough points to cause splits
        for i in range(20):
            tree.insert(float(i), 0.0, f"point_{i}")

        # Tree should have split multiple times
        assert tree.height > 1

        # KNN should still work correctly
        results = tree.knn(10.0, 0.0, 3)

        assert len(results) == 3
        assert results[0][0] == "point_10"
        assert results[0][1] == 0.0
        # Second and third nearest should be point_9 and point_11 (distance 1)
        # or point_12 if there's a tie-breaking scenario
        assert results[1][1] <= results[2][1]
        # Check distances are correct
        assert results[1][1] <= 2.0
        assert results[2][1] <= 2.0

    def test_knn_diagonal_distances(self) -> None:
        """Test KNN with diagonal distances."""
        tree = RTree()

        # Create points along different diagonals
        tree.insert(1.0, 1.0, "A")  # Distance sqrt(2) from origin
        tree.insert(2.0, 2.0, "B")  # Distance 2*sqrt(2) from origin
        tree.insert(1.0, 0.0, "C")  # Distance 1 from origin
        tree.insert(0.0, 1.0, "D")  # Distance 1 from origin

        results = tree.knn(0.0, 0.0, 2)

        assert len(results) == 2
        # C and D should be nearest (both distance 1)
        assert set([results[0][0], results[1][0]]) == {"C", "D"}
        assert abs(results[0][1] - 1.0) < 0.001
        assert abs(results[1][1] - 1.0) < 0.001

    def test_knn_single_k(self) -> None:
        """Test KNN with k=1."""
        tree = RTree()

        tree.insert(1.0, 1.0, "A")
        tree.insert(2.0, 2.0, "B")
        tree.insert(3.0, 3.0, "C")

        results = tree.knn(0.0, 0.0, 1)

        assert len(results) == 1
        assert results[0][0] == "A"

    def test_knn_query_at_data_point(self) -> None:
        """Test KNN with query point exactly at a data point."""
        tree = RTree()

        tree.insert(5.0, 5.0, "exact")
        tree.insert(6.0, 5.0, "near1")
        tree.insert(5.0, 6.0, "near2")
        tree.insert(10.0, 10.0, "far")

        results = tree.knn(5.0, 5.0, 2)

        assert len(results) == 2
        assert results[0][0] == "exact"
        assert results[0][1] == 0.0
        assert results[1][0] in ["near1", "near2"]

    def test_knn_clustered_points(self) -> None:
        """Test KNN with clustered points."""
        tree = RTree()

        # Cluster 1: around (0, 0)
        tree.insert(0.0, 0.0, "c1_1")
        tree.insert(0.1, 0.1, "c1_2")
        tree.insert(0.2, 0.2, "c1_3")

        # Cluster 2: around (10, 10)
        tree.insert(10.0, 10.0, "c2_1")
        tree.insert(10.1, 10.1, "c2_2")
        tree.insert(10.2, 10.2, "c2_3")

        # Query near cluster 1
        results = tree.knn(0.0, 0.0, 3)

        assert len(results) == 3
        # All results should be from cluster 1
        for data, _ in results:
            assert data.startswith("c1")

    def test_knn_returns_tuples(self) -> None:
        """Test that KNN returns tuples of (data, distance)."""
        tree = RTree()

        tree.insert(1.0, 0.0, "A")
        tree.insert(2.0, 0.0, "B")

        results = tree.knn(0.0, 0.0, 2)

        assert len(results) == 2
        assert isinstance(results[0], tuple)
        assert len(results[0]) == 2
        assert isinstance(results[0][1], float)
