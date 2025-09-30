"""R-tree implementation for spatial indexing."""

from typing import Any

from rtree.rectangle import Rectangle
from rtree.rtree_node import RTreeNode


class RTree:
    """R-tree for spatial indexing."""

    def __init__(self, max_entries: int = 4, verbose: bool = False):
        """Initialize an R-tree."""
        self.root: RTreeNode | None = None
        self.max_entries = max_entries
        self.height = 0
        self.verbose = verbose  # Flag to control printing after insertions

    def insert(self, x: float, y: float, data: Any = None) -> None:
        """Insert a point with associated data."""
        # Create MBR for the point (point is a degenerate rectangle)
        mbr = Rectangle(x, y, x, y)

        # Check if tree is empty
        if self.root is None:
            self.root = RTreeNode(is_leaf=True, max_entries=self.max_entries)
            self.root.add_entry(mbr, data)
            self.height = 1
            if self.verbose:
                print(f"\n📍 Inserted: {data} at ({x}, {y})")
                print("Tree after insertion:")
                print(self)
            return

        # Find appropriate leaf node
        leaf = self.root.choose_subtree(mbr)

        # Insert object into leaf node
        leaf.add_entry(mbr, data)

        # Check for overflow and handle splitting
        old_height = self.height
        self._handle_overflow(leaf)

        # Update MBRs up to root
        leaf.update_mbr_upward()

        if self.verbose:
            print(f"\n📍 Inserted: {data} at ({x}, {y})")
            if self.height > old_height:
                print("⚠️  Tree height increased! Rebalancing occurred.")
            print("Tree after insertion:")
            print(self)

    def _handle_overflow(self, node: RTreeNode) -> None:
        """Handle node overflow by splitting if necessary."""
        if not node.is_full():
            return

        # Split the node
        node1, node2 = node.quadratic_split()

        # If node has no parent (is root), create new root
        if node.parent is None:
            new_root = RTreeNode(is_leaf=False, max_entries=self.max_entries)
            new_root.add_entry(node1.mbr, node1)
            new_root.add_entry(node2.mbr, node2)

            node1.parent = new_root
            node2.parent = new_root

            self.root = new_root
            self.height += 1
        else:
            # Insert new node reference in parent
            parent = node.parent
            parent.add_entry(node2.mbr, node2)
            node2.parent = parent

            # Check for parent overflow (propagate split upward)
            self._handle_overflow(parent)

    def search_point(self, x: float, y: float) -> list[Any]:
        """Search for entries containing a specific point."""
        if self.root is None:
            return []

        query_rect = Rectangle(x, y, x, y)
        return self.root.search(query_rect)

    def search_rectangle(
        self,
        x_min: float,
        y_min: float,
        x_max: float,
        y_max: float,
    ) -> list[Any]:
        """Search for entries intersecting with a rectangle."""
        if self.root is None:
            return []

        query_rect = Rectangle(x_min, y_min, x_max, y_max)
        return self.root.search(query_rect)

    def print_tree(self, node: RTreeNode | None = None, level: int = 0) -> None:
        """Print tree structure for debugging."""
        if node is None:
            node = self.root
            print(f"R-tree (height={self.height}, max_entries={self.max_entries})")

        if node is None:
            print("  " * level + "Empty tree")
            return

        prefix = "  " * level
        node_type = "Leaf" if node.is_leaf else "Internal"
        print(f"{prefix}{node_type} Node (entries={len(node.entries)}, mbr={node.mbr})")

        for mbr, data in node.entries:
            if node.is_leaf:
                print(f"{prefix}  Entry: mbr={mbr}, data={data}")
            else:
                self.print_tree(data, level + 1)

    def __str__(self) -> str:
        """Return a tree-like string representation."""
        lines = []
        lines.append(f"RTree (height={self.height}, max_entries={self.max_entries})")
        if self.root is None:
            lines.append("└── Empty")
        else:
            root_lines = self.root.get_tree_lines("", True)
            # Replace the first line to show it's the root
            if root_lines:
                root_lines[0] = "└── Root" + root_lines[0][3:]
            lines.extend(root_lines)
        return "\n".join(lines)
