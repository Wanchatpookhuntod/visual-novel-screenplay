# Branch Node Updates Summary

## Changes Made:

### 1. Default Output Count
- Changed from 3 outputs to 1 output by default
- Branch nodes now start with a single output circle

### 2. Removed + and - Buttons
- Removed BranchButton class integration
- Removed physical + and - buttons from Branch nodes
- Removed update_button_visibility() method

### 3. Added Context Menu for Output Management
- Right-click on Branch node shows context menu
- Added "➕ Add Output" option (disabled when max 8 outputs reached)
- Added "➖ Remove Output" option (disabled when only 1 output remaining)
- Context menu includes Edit, Duplicate, Add/Remove Output, and Delete options

### 4. Improved Output Positioning
- Output circles now start from the top of the node (15px margin)
- Fixed spacing of 25px between outputs
- No more dynamic repositioning - outputs stay in fixed positions
- Added outputs appear below existing ones

### 5. Fixed InputOutputCircle
- Added connected_edges = [] initialization in constructor
- Proper edge management when adding/removing outputs

### 6. Updated View Event Handling
- Modified views.py to allow right-click on Branch nodes
- Right-click on empty areas still shows node creation menu
- Right-click on Branch nodes shows their specific context menu

## Usage:
1. Right-click on empty area → Create Branch Node (starts with 1 output)
2. Right-click on Branch node → Add/Remove Output options
3. Outputs are positioned from top to bottom with consistent spacing
