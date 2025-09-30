"""Rectangle class for R-tree implementation."""

from dataclasses import dataclass
from typing import Self


@dataclass
class Rectangle:
    """Represents a bounding rectangle (MBR - Minimum Bounding Rectangle)."""

    x_min: float
    y_min: float
    x_max: float
    y_max: float

    def area(self: Self) -> float:
        """Calculate the area of the rectangle."""
        return (self.x_max - self.x_min) * (self.y_max - self.y_min)

    def enlargement_needed(self: Self, other: "Rectangle") -> float:
        """Calculate area enlargement needed to include another rectangle."""
        enlarged = self.union(other)
        return enlarged.area() - self.area()

    def union(self: Self, other: "Rectangle") -> "Rectangle":
        """Return the MBR that contains both rectangles."""
        return Rectangle(
            min(self.x_min, other.x_min),
            min(self.y_min, other.y_min),
            max(self.x_max, other.x_max),
            max(self.y_max, other.y_max),
        )

    def intersects(self: Self, other: "Rectangle") -> bool:
        """Check if this rectangle intersects with another."""
        return not (
            self.x_max < other.x_min
            or self.x_min > other.x_max
            or self.y_max < other.y_min
            or self.y_min > other.y_max
        )

    def contains_point(self: Self, x: float, y: float) -> bool:
        """Check if a point is within this rectangle."""
        return self.x_min <= x <= self.x_max and self.y_min <= y <= self.y_max

    def __str__(self: Self) -> str:
        """Return a string representation of the rectangle."""
        if self.x_min == self.x_max and self.y_min == self.y_max:
            return f"({self.x_min:.0f},{self.y_min:.0f})"
        return (
            f"[({self.x_min:.0f},{self.y_min:.0f})-({self.x_max:.0f},{self.y_max:.0f})]"
        )
