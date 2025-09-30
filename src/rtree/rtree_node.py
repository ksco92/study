"""RTree node implementation for spatial indexing."""

from typing import Any

from rtree.rectangle import Rectangle


class RTreeNode:
    """Node in an R-tree."""

    def __init__(self, is_leaf: bool = True, max_entries: int = 4):
        """Initialize an R-tree node."""
        self.is_leaf = is_leaf
        self.entries = []  # List of (MBR, data/child_node) tuples
        self.parent: RTreeNode | None = None
        self.max_entries = max_entries
        self.min_entries = max_entries // 2

    @property
    def mbr(self) -> Rectangle | None:
        """Calculate the MBR for this node from its entries."""
        if not self.entries:
            return None

        # Start with the first entry's MBR
        result = self.entries[0][0]

        # Union with all other entries
        for mbr, _ in self.entries[1:]:
            result = result.union(mbr)

        return result

    def is_full(self) -> bool:
        """Check if node has reached maximum capacity."""
        return len(self.entries) > self.max_entries

    def choose_subtree(self, new_mbr: Rectangle) -> "RTreeNode":
        """Choose the best child node for inserting a new entry."""
        if self.is_leaf:
            return self

        best_child = None
        min_enlargement = float("inf")
        min_area = float("inf")

        # Select child with minimum bounding box enlargement
        for mbr, child in self.entries:
            enlargement = mbr.enlargement_needed(new_mbr)
            area = mbr.area()

            # Choose based on minimum enlargement, break ties by smallest area
            if enlargement < min_enlargement or (
                enlargement == min_enlargement and area < min_area
            ):
                min_enlargement = enlargement
                min_area = area
                best_child = child

        # Recursively descend to leaf level
        if best_child is None:
            raise ValueError("No child node found for insertion")
        return best_child.choose_subtree(new_mbr)

    def add_entry(self, mbr: Rectangle, data: Any) -> None:
        """Add an entry to this node."""
        self.entries.append((mbr, data))

    def quadratic_split(self) -> tuple["RTreeNode", "RTreeNode"]:
        """Split node using quadratic algorithm.

        Returns two nodes with distributed entries.
        """
        # Create new node
        new_node = RTreeNode(self.is_leaf, self.max_entries)

        # Find two entries that would waste the most area if grouped
        max_waste = -1
        seed1_idx, seed2_idx = 0, 1

        for i in range(len(self.entries)):
            for j in range(i + 1, len(self.entries)):
                mbr1, mbr2 = self.entries[i][0], self.entries[j][0]
                union_area = mbr1.union(mbr2).area()
                waste = union_area - mbr1.area() - mbr2.area()

                if waste > max_waste:
                    max_waste = waste
                    seed1_idx, seed2_idx = i, j

        # Start groups with seed entries
        group1 = [self.entries[seed1_idx]]
        group2 = [self.entries[seed2_idx]]
        group1_mbr = self.entries[seed1_idx][0]
        group2_mbr = self.entries[seed2_idx][0]

        # Distribute remaining entries
        remaining = [
            e for i, e in enumerate(self.entries) if i not in (seed1_idx, seed2_idx)
        ]

        while remaining:
            if (
                len(group1) >= self.min_entries
                and len(remaining) + len(group2) == self.min_entries
            ):
                # Must assign all remaining to group2 to maintain minimum
                group2.extend(remaining)
                break
            if (
                len(group2) >= self.min_entries
                and len(remaining) + len(group1) == self.min_entries
            ):
                # Must assign all remaining to group1 to maintain minimum
                group1.extend(remaining)
                break

            # Choose entry with maximum difference in enlargement
            max_diff = -1
            best_entry = None
            best_group = None

            for entry in remaining:
                mbr = entry[0]
                enlarge1 = group1_mbr.enlargement_needed(mbr)
                enlarge2 = group2_mbr.enlargement_needed(mbr)
                diff = abs(enlarge1 - enlarge2)

                if diff > max_diff:
                    max_diff = diff
                    best_entry = entry
                    best_group = 1 if enlarge1 < enlarge2 else 2

            # Add to chosen group and update MBR
            if best_entry is not None:
                if best_group == 1:
                    group1.append(best_entry)
                    group1_mbr = group1_mbr.union(best_entry[0])
                else:
                    group2.append(best_entry)
                    group2_mbr = group2_mbr.union(best_entry[0])

                remaining.remove(best_entry)

        # Update nodes with distributed entries
        self.entries = group1
        new_node.entries = group2

        # Update parent references for non-leaf nodes
        if not self.is_leaf:
            for _, child in self.entries:
                child.parent = self
            for _, child in new_node.entries:
                child.parent = new_node

        return self, new_node

    def update_mbr_upward(self) -> None:
        """Update MBRs propagating changes up to root."""
        if self.parent:
            # Find this node in parent's entries and update its MBR
            for i, (_, child) in enumerate(self.parent.entries):
                if child == self:
                    self.parent.entries[i] = (self.mbr, self)
                    break

            # Continue propagating upward
            self.parent.update_mbr_upward()

    def search(self, query_rect: Rectangle) -> list[Any]:
        """Search for all entries intersecting with query rectangle."""
        results = []

        for mbr, data in self.entries:
            if mbr.intersects(query_rect):
                if self.is_leaf:
                    # Return actual data for leaf entries
                    results.append(data)
                else:
                    # Recursively search child nodes
                    results.extend(data.search(query_rect))

        return results

    def get_tree_lines(self, prefix: str = "", is_last: bool = True) -> list[str]:
        """Generate tree representation lines."""
        lines = []

        # Current node line
        connector = "└── " if is_last else "├── "
        node_type = "Leaf" if self.is_leaf else "Node"
        mbr_str = str(self.mbr) if self.mbr else "Empty"
        lines.append(f"{prefix}{connector}{node_type} {mbr_str}")

        # Update prefix for children
        extension = "    " if is_last else "│   "
        new_prefix = prefix + extension

        # Add entries
        for i, (mbr, data) in enumerate(self.entries):
            is_last_entry = i == len(self.entries) - 1
            if self.is_leaf:
                entry_connector = "└── " if is_last_entry else "├── "
                data_str = str(data) if data else "None"
                lines.append(f"{new_prefix}{entry_connector}• {str(mbr)}: {data_str}")
            else:
                # Recursively add child node
                child_lines = data.get_tree_lines(new_prefix, is_last_entry)
                lines.extend(child_lines)

        return lines

    def __str__(self) -> str:
        """Return a tree-like string representation."""
        lines = self.get_tree_lines("", True)
        return "\n".join(lines)
