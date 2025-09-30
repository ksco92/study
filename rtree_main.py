"""RTree usage example."""

from rtree.rtree import RTree

# Create RTree with verbose=True to see tree after each insertion
rtree = RTree(max_entries=3, verbose=True)

"""
  Y
 10 |                                 
  9 |                J                
  8 |                      F          
  7 |             D                   
  6 |                            C    
  5 |          H                      
  4 |                B                
  3 |       A                         
  2 |    G              I             
  1 |                         E       
  0 |                                 
    +---------------------------------
     0  1  2  3  4  5  6  7  8  9 10  X
"""

# Insert some points
points = [
    (2, 3, "Restaurant A"),
    (5, 4, "Restaurant B"),
    (9, 6, "Store C"),
    (4, 7, "Store D"),
    (8, 1, "Park E"),
    (7, 8, "Museum F"),
    (1, 2, "Cafe G"),
    (3, 5, "Library H"),
    (6, 2, "Bank I"),
    (5, 9, "Hospital J"),
]

print("\n" + "=" * 50)
print("INSERTING POINTS INTO R-TREE (with tree visualization after each insertion)")
print("=" * 50)

for x, y, name in points:
    rtree.insert(x, y, name)

print("\n" + "=" * 50)
print("FINAL TREE STRUCTURE:")
print("=" * 50)
print(rtree)

print("\n" + "=" * 50)
print("Searching for points in rectangle (3, 3) to (7, 7):")
results = rtree.search_rectangle(3, 3, 7, 7)
for result in results:
    print(f"  Found: {result}")

print("\n" + "=" * 50)
print("Searching for exact point (5, 4):")
results = rtree.search_point(5, 4)
for result in results:
    print(f"  Found: {result}")

print("\n" + "=" * 50)
print("Searching for KNN for (10, 1) with k = 4:")
results = rtree.knn(10, 0, 4)
for result in results:
    print(f"  Found: {result}")
