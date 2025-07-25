# Dynamic Branch Node Updates

## Key Changes:

### 1. Dynamic Height Calculation
- Node height is calculated based on number of outputs
- Formula: `(num_outputs - 1) * spacing + 2 * margin`
- Default spacing: 25px between outputs
- Top/bottom margin: 20px

### 2. Centered Output Positioning
- Single output: positioned at center of node
- Multiple outputs: distributed evenly around center
- Input circle always at vertical center (left side)

### 3. Automatic Resizing
- `resize_node_for_outputs(num_outputs)` method
- Resizes node rectangle
- Repositions input circle to new center
- Recreates all output circles with new positions

### 4. Connection Preservation
- Stores existing connections before resizing
- Restores connections after recreating circles
- Updates edge positions automatically

### 5. Constructor Changes
- Takes optional height parameter
- Calculates initial height for 1 output
- Calls `create_output_circles()` method

## Methods Added:
- `calculate_height_for_outputs(num_outputs)` - calculates required height
- `create_output_circles(num_outputs)` - creates positioned output circles
- `resize_node_for_outputs(num_outputs)` - resizes node and repositions circles

## Behavior:
1. **1 Output**: Node is compact, output at center
2. **2+ Outputs**: Node grows taller, outputs centered vertically
3. **Add Output**: Node expands, outputs redistribute
4. **Remove Output**: Node shrinks, remaining outputs reposition
5. **Connections**: Preserved through resize operations

## Constants:
- `output_spacing = 25` - distance between output circles
- `top_bottom_margin = 20` - margin from top/bottom edges
- `circle_radius = 6` - radius of input/output circles
