"""Unit tests for Rectangle class."""

from rtree.rectangle import Rectangle


class TestRectangle:
    """Test cases for Rectangle class."""

    def test_rectangle_creation(self) -> None:
        """Test creating a rectangle."""
        rect = Rectangle(1.0, 2.0, 3.0, 4.0)
        assert rect.x_min == 1.0
        assert rect.y_min == 2.0
        assert rect.x_max == 3.0
        assert rect.y_max == 4.0

    def test_point_rectangle(self) -> None:
        """Test creating a degenerate rectangle (point)."""
        rect = Rectangle(5.0, 5.0, 5.0, 5.0)
        assert rect.x_min == rect.x_max == 5.0
        assert rect.y_min == rect.y_max == 5.0

    def test_area_calculation(self) -> None:
        """Test area calculation."""
        rect1 = Rectangle(0.0, 0.0, 4.0, 3.0)
        assert rect1.area() == 12.0

        rect2 = Rectangle(2.0, 2.0, 2.0, 2.0)  # Point
        assert rect2.area() == 0.0

        rect3 = Rectangle(-2.0, -3.0, 2.0, 3.0)
        assert rect3.area() == 24.0

    def test_enlargement_needed(self) -> None:
        """Test enlargement calculation."""
        rect1 = Rectangle(0.0, 0.0, 2.0, 2.0)  # Area = 4
        rect2 = Rectangle(3.0, 3.0, 4.0, 4.0)  # Area = 1

        # Union would be (0,0) to (4,4) with area = 16
        # Enlargement = 16 - 4 = 12
        assert rect1.enlargement_needed(rect2) == 12.0

        # Enlargement for overlapping rectangles
        rect3 = Rectangle(1.0, 1.0, 3.0, 3.0)
        # Union would be (0,0) to (3,3) with area = 9
        # Enlargement = 9 - 4 = 5
        assert rect1.enlargement_needed(rect3) == 5.0

        # No enlargement needed when one contains the other
        rect4 = Rectangle(0.5, 0.5, 1.5, 1.5)
        assert rect1.enlargement_needed(rect4) == 0.0

    def test_union(self) -> None:
        """Test union of two rectangles."""
        rect1 = Rectangle(0.0, 0.0, 2.0, 2.0)
        rect2 = Rectangle(1.0, 1.0, 3.0, 3.0)

        union = rect1.union(rect2)
        assert union.x_min == 0.0
        assert union.y_min == 0.0
        assert union.x_max == 3.0
        assert union.y_max == 3.0

        # Union with disjoint rectangles
        rect3 = Rectangle(5.0, 5.0, 6.0, 6.0)
        union2 = rect1.union(rect3)
        assert union2.x_min == 0.0
        assert union2.y_min == 0.0
        assert union2.x_max == 6.0
        assert union2.y_max == 6.0

    def test_intersects(self) -> None:
        """Test rectangle intersection."""
        rect1 = Rectangle(0.0, 0.0, 2.0, 2.0)
        rect2 = Rectangle(1.0, 1.0, 3.0, 3.0)
        rect3 = Rectangle(3.0, 3.0, 4.0, 4.0)

        # Overlapping rectangles
        assert rect1.intersects(rect2) is True
        assert rect2.intersects(rect1) is True

        # Non-overlapping rectangles
        assert rect1.intersects(rect3) is False
        assert rect3.intersects(rect1) is False

        # Edge-touching rectangles (edge-touching is considered intersection in this implementation)
        rect4 = Rectangle(2.0, 0.0, 3.0, 2.0)
        assert rect1.intersects(rect4) is True  # Edge touching counts as intersection

        # Truly non-overlapping rectangles
        rect5 = Rectangle(2.1, 0.0, 3.0, 2.0)
        assert rect1.intersects(rect5) is False  # No overlap

        # Point intersection
        point = Rectangle(1.0, 1.0, 1.0, 1.0)
        assert rect1.intersects(point) is True

    def test_contains_point(self) -> None:
        """Test if rectangle contains a point."""
        rect = Rectangle(0.0, 0.0, 10.0, 10.0)

        # Inside points
        assert rect.contains_point(5.0, 5.0) is True
        assert rect.contains_point(0.0, 0.0) is True  # On corner
        assert rect.contains_point(10.0, 10.0) is True  # On opposite corner
        assert rect.contains_point(5.0, 0.0) is True  # On edge

        # Outside points
        assert rect.contains_point(-1.0, 5.0) is False
        assert rect.contains_point(11.0, 5.0) is False
        assert rect.contains_point(5.0, -1.0) is False
        assert rect.contains_point(5.0, 11.0) is False

    def test_str_representation(self) -> None:
        """Test string representation."""
        rect1 = Rectangle(1.0, 2.0, 3.0, 4.0)
        assert str(rect1) == "[(1,2)-(3,4)]"

        point = Rectangle(5.0, 5.0, 5.0, 5.0)
        assert str(point) == "(5,5)"

    def test_negative_coordinates(self) -> None:
        """Test rectangles with negative coordinates."""
        rect = Rectangle(-5.0, -3.0, -1.0, -1.0)
        assert rect.area() == 8.0

        assert rect.contains_point(-2.0, -2.0) is True

    def test_union_with_self(self) -> None:
        """Test union of rectangle with itself."""
        rect = Rectangle(1.0, 2.0, 3.0, 4.0)
        union = rect.union(rect)
        assert union.x_min == rect.x_min
        assert union.y_min == rect.y_min
        assert union.x_max == rect.x_max
        assert union.y_max == rect.y_max

    def test_float_precision(self) -> None:
        """Test with floating point precision."""
        rect1 = Rectangle(0.1, 0.1, 0.3, 0.3)
        rect2 = Rectangle(0.2, 0.2, 0.4, 0.4)

        union = rect1.union(rect2)
        assert union.x_min == 0.1
        assert union.x_max == 0.4

        # Area calculation with floats
        assert abs(rect1.area() - 0.04) < 1e-10
