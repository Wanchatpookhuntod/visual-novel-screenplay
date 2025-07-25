# Edge Update Fix for Branch Node

## Problem Fixed:
When Branch node resizes (add/remove outputs), the input circle moves to new center position, but connected edges don't update their positions immediately.

## Solution Applied:

### 1. Enhanced `resize_node_for_outputs()` method:
- Added immediate edge updates for input circle after repositioning
- Added edge updates for all output circles after recreation
- Added scene.update() call to force visual refresh

### 2. Enhanced `add_output_circle()` method:
- Store input connections separately before resizing
- Restore input connections after resizing
- Explicitly update input edges with updateFromNodes()
- Maintain existing output connection restoration

### 3. Enhanced `remove_output_circle()` method:
- Store input connections separately before resizing
- Restore input connections after resizing
- Explicitly update input edges with updateFromNodes()
- Maintain existing output connection restoration

## Key Changes:

### Input Connection Preservation:
```python
# Store input connections separately
input_connections = []
if hasattr(self.input_circle, 'connected_edges'):
    input_connections = self.input_circle.connected_edges[:]

# Restore input connections
if input_connections:
    if not hasattr(self.input_circle, 'connected_edges'):
        self.input_circle.connected_edges = []
    self.input_circle.connected_edges = input_connections
    
    # Update input edges
    for edge in input_connections:
        if hasattr(edge, 'updateFromNodes'):
            edge.updateFromNodes()
```

### Immediate Edge Updates in resize_node_for_outputs():
```python
# Update connected edges for input circle immediately
if hasattr(self.input_circle, 'connected_edges'):
    for edge in self.input_circle.connected_edges:
        if hasattr(edge, 'updateFromNodes'):
            edge.updateFromNodes()

# Update all connected edges for output circles
for circle in self.output_circles:
    if hasattr(circle, 'connected_edges'):
        for edge in circle.connected_edges:
            if hasattr(edge, 'updateFromNodes'):
                edge.updateFromNodes()
```

## Result:
- Input edges now update position immediately when Branch node resizes
- Output edges maintain their connections and update positions correctly
- Visual updates are forced with scene.update() calls
- All edge positions stay synchronized with node changes
