"""
Graphics Items for Visual Novel Node Editor
Contains all graphics-related classes: InputOutputCircle, EdgeGraphicsItem, NodeScene, StartNode, BranchNode
Plus helper classes for interactive buttons
"""

import time
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsPathItem, QDialog, QMenu, QGraphicsTextItem
from PySide6.QtGui import QBrush, QColor, QPainterPath, QPen, QCursor, QFont
from PySide6.QtCore import Qt, QPointF

# Import form from local module
from form import MyForm


class BranchButton(QGraphicsEllipseItem):
    """Clickable button for branch node operations"""
    def __init__(self, x, y, radius, text, parent, callback):
        super().__init__(x - radius, y - radius, radius * 2, radius * 2, parent)
        self.callback = callback
        self.text = text
        self.radius = radius
        
        # Style the button
        self.setBrush(QBrush(QColor(70, 70, 70)))  # Dark gray background
        self.setPen(QPen(QColor(200, 200, 200), 2))  # Light gray border
        self.setZValue(3)  # Above other elements
        self.setAcceptHoverEvents(True)
        
        # Create text label
        self.text_item = QGraphicsTextItem(text, self)
        font = QFont("Arial", 10, QFont.Bold)
        self.text_item.setFont(font)
        self.text_item.setDefaultTextColor(QColor(255, 255, 255))  # White text
        
        # Center the text
        text_rect = self.text_item.boundingRect()
        self.text_item.setPos(-text_rect.width()/2, -text_rect.height()/2)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Execute callback when clicked
            if self.callback:
                self.callback()
            event.accept()
        else:
            event.ignore()
            
    def hoverEnterEvent(self, event):
        # Highlight on hover
        self.setBrush(QBrush(QColor(100, 100, 100)))
        self.setPen(QPen(QColor(255, 255, 255), 2))
        event.accept()
        
    def hoverLeaveEvent(self, event):
        # Return to normal color
        self.setBrush(QBrush(QColor(70, 70, 70)))
        self.setPen(QPen(QColor(200, 200, 200), 2))
        event.accept()


class InputOutputCircle(QGraphicsEllipseItem):
    def __init__(self, x, y, w, h, parent, point_type):
        super().__init__(x, y, w, h, parent)
        # Set different colors for input and output
        if point_type == 'input':
            self.setBrush(QBrush(QColor(255, 100, 100)))  # Light red for input
        else:
            self.setBrush(QBrush(QColor(100, 150, 255)))  # Light blue for output
        self.setPen(QColor(0, 0, 0))
        self.setAcceptHoverEvents(True)
        self.setAcceptedMouseButtons(Qt.AllButtons)
        self.setFlag(QGraphicsEllipseItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsEllipseItem.ItemIsFocusable, True)
        self.point_type = point_type  # 'input' or 'output'
        self._drag_edge = None
        self.connected_edges = []  # Initialize connected edges list

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            scene = self.scene()
            if scene:
                start_pos = self.mapToScene(self.rect().center())
                # Set edge color based on point type during drag
                if self.point_type == 'output':
                    color = QColor(0, 150, 255)  # Blue for output
                else:
                    color = QColor(255, 0, 0)    # Red for input
                self._drag_edge = EdgeGraphicsItem(start_pos, start_pos, color)
                scene.addItem(self._drag_edge)
                self.grabMouse()  # Ensure this item receives all mouse move/release events
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        if self._drag_edge is not None:
            scene = self.scene()
            if scene:
                # Get mouse position in scene coordinates directly
                mouse_scene_pos = self.mapToScene(event.pos())
                self._drag_edge.setEndPos(mouse_scene_pos)
            event.accept()
        else:
            event.ignore()

    def mouseReleaseEvent(self, event):
        if self._drag_edge is not None:
            scene = self.scene()
            if scene:
                # Check if released on another InputOutputCircle
                # Get mouse position in scene coordinates directly
                mouse_scene_pos = self.mapToScene(event.pos())
                items = scene.items(mouse_scene_pos)
                target_circle = None
                for item in items:
                    if isinstance(item, InputOutputCircle) and item is not self:
                        # Check if connection is valid: output can only connect to input and vice versa
                        if ((self.point_type == 'output' and item.point_type == 'input') or 
                            (self.point_type == 'input' and item.point_type == 'output')):
                            target_circle = item
                            break
                
                if target_circle:
                    # Create persistent edge between self and target_circle
                    start_pos = self.mapToScene(self.rect().center())
                    end_pos = target_circle.mapToScene(target_circle.rect().center())
                    # Color: blue if from output, red if from input
                    if self.point_type == 'output':
                        color = QColor(0, 150, 255)
                    else:
                        color = QColor(255, 0, 0)
                    # Create edge with node references
                    edge = EdgeGraphicsItem(start_pos, end_pos, color, None, self, target_circle)
                    scene.addItem(edge)
                    
                    # Store edge references in both circles for tracking
                    if not hasattr(self, 'connected_edges'):
                        self.connected_edges = []
                    if not hasattr(target_circle, 'connected_edges'):
                        target_circle.connected_edges = []
                    self.connected_edges.append(edge)
                    target_circle.connected_edges.append(edge)
                    
                    # Update connection tracking for both nodes
                    self_node = self.parentItem()
                    target_node = target_circle.parentItem()
                    if isinstance(self_node, (NodeScene, StartNode, BranchNode)):
                        self_node.updateConnectionTracking()
                    if isinstance(target_node, (NodeScene, StartNode, BranchNode)):
                        target_node.updateConnectionTracking()
                else:
                    # No target circle found - create new node at drop position
                    self.create_connected_node(mouse_scene_pos)
                
                scene.removeItem(self._drag_edge)
            self._drag_edge = None
        self.ungrabMouse()  # Release mouse grab
        event.accept()

    def create_connected_node(self, position):
        """Create a new node at the specified position and connect to it"""
        scene = self.scene()
        if not scene:
            return
        
        # Get main window for access to node_items list
        main_window = None
        for view in scene.views():
            main_window = view.window()
            break
        
        if main_window and hasattr(main_window, 'node_items'):
            # Create new node at drop position
            new_node = NodeScene(position.x() - 60, position.y() - 30)  # Center node at position
            scene.addItem(new_node)
            main_window.node_items.append(new_node)
            
            # Connect based on the type of circle we dragged from
            if self.point_type == 'output':
                # Dragged from output, connect to new node's input
                target_circle = new_node.input_circle
                start_pos = self.mapToScene(self.rect().center())
                end_pos = target_circle.mapToScene(target_circle.rect().center())
                color = QColor(0, 150, 255)  # Blue for output
            else:
                # Dragged from input, connect to new node's output
                target_circle = new_node.output_circle
                start_pos = target_circle.mapToScene(target_circle.rect().center())
                end_pos = self.mapToScene(self.rect().center())
                color = QColor(255, 0, 0)  # Red for input
            
            # Create the edge
            edge = EdgeGraphicsItem(start_pos, end_pos, color, None, 
                                  self if self.point_type == 'output' else target_circle,
                                  target_circle if self.point_type == 'output' else self)
            scene.addItem(edge)
            
            # Store edge references in both circles
            if not hasattr(self, 'connected_edges'):
                self.connected_edges = []
            if not hasattr(target_circle, 'connected_edges'):
                target_circle.connected_edges = []
            self.connected_edges.append(edge)
            target_circle.connected_edges.append(edge)
            
            # Update connection tracking for both nodes
            self_node = self.parentItem()
            if isinstance(self_node, (NodeScene, StartNode, BranchNode)):
                self_node.updateConnectionTracking()
            if isinstance(new_node, (NodeScene, StartNode, BranchNode)):
                new_node.updateConnectionTracking()
            
            # Update scene rect to include new node
            node_rect = new_node.sceneBoundingRect()
            scene_rect = scene.sceneRect()
            offset = 40
            node_rect = node_rect.adjusted(-offset, -offset, offset, offset)
            new_rect = scene_rect.united(node_rect)
            scene.setSceneRect(new_rect)
            
            # Show status message
            if hasattr(main_window, 'status_bar'):
                main_window.status_bar.showMessage(f"Created and connected new node '{new_node.name}'", 3000)
            
            print(f"Auto-created node '{new_node.name}' and connected via {self.point_type} circle")


class EdgeGraphicsItem(QGraphicsPathItem):
    def __init__(self, start_pos, end_pos, color=None, parent=None, start_circle=None, end_circle=None):
        super().__init__(parent)
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.start_circle = start_circle  # Reference to start InputOutputCircle
        self.end_circle = end_circle      # Reference to end InputOutputCircle
        self.setZValue(-2)  # Make sure edge is below nodes and input/output circles
        # If color is not specified, use blue for output, red for input
        if color is None:
            color = QColor(255, 0, 0)  # Red fiber
        self.pen = QPen(color, 3)
        self.setPen(self.pen)
        self.updatePath()
        
        # Make edge selectable
        self.setFlag(QGraphicsPathItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsPathItem.ItemIsFocusable, True)

    def setEndPos(self, pos):
        self.end_pos = pos
        self.updatePath()

    def setStartPos(self, pos):
        self.start_pos = pos
        self.updatePath()

    def updateFromNodes(self):
        """Update edge position based on connected nodes"""
        if self.start_circle and self.end_circle:
            self.start_pos = self.start_circle.mapToScene(self.start_circle.rect().center())
            self.end_pos = self.end_circle.mapToScene(self.end_circle.rect().center())
            self.updatePath()

    def updatePath(self):
        path = QPainterPath(self.start_pos)
        
        # Calculate control points for proper curve direction
        dx = self.end_pos.x() - self.start_pos.x()
        dy = self.end_pos.y() - self.start_pos.y()
        
        # Use tension factor for curve strength
        tension = 0.5  # Adjustable tension (0.0 = straight, 1.0 = maximum curve)
        
        # Calculate minimum offset to ensure visible curve
        min_offset = 80  # Minimum curve offset
        distance = abs(dx)
        
        # Calculate horizontal offset based on distance and tension
        h_offset = max(min_offset, distance * tension)
        
        # Always curve outward regardless of direction
        # This creates natural-looking curves in both directions
        c1 = self.start_pos + QPointF(h_offset, 0)
        c2 = self.end_pos - QPointF(h_offset, 0)
        
        path.cubicTo(c1, c2, self.end_pos)
        self.setPath(path)

    def paint(self, painter, option, widget=None):
        # Change color when selected
        if self.isSelected():
            selected_pen = QPen(QColor(255, 255, 0), 4)  # Yellow when selected
            painter.setPen(selected_pen)
        else:
            painter.setPen(self.pen)
        painter.drawPath(self.path())

    def removeFromConnections(self):
        """Remove this edge from connected circles' edge lists"""
        if self.start_circle and hasattr(self.start_circle, 'connected_edges'):
            if self in self.start_circle.connected_edges:
                self.start_circle.connected_edges.remove(self)
        if self.end_circle and hasattr(self.end_circle, 'connected_edges'):
            if self in self.end_circle.connected_edges:
                self.end_circle.connected_edges.remove(self)
        
        # Update connection tracking for both nodes
        if self.start_circle:
            start_node = self.start_circle.parentItem()
            if isinstance(start_node, (NodeScene, StartNode, BranchNode)):
                start_node.updateConnectionTracking()
        if self.end_circle:
            end_node = self.end_circle.parentItem()
            if isinstance(end_node, (NodeScene, StartNode, BranchNode)):
                end_node.updateConnectionTracking()


class NodeScene(QGraphicsRectItem):
    def __init__(self, x, y, w=120, h=60, name=None):
        super().__init__(0, 0, w, h)
        self.setPos(x, y)
        self.setBrush(QBrush(QColor(200, 200, 200)))
        self.setPen(QColor(0, 255, 0))
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsRectItem.ItemIsFocusable, True)
        self.setAcceptHoverEvents(True)
        self.setZValue(0)  # Node at middle layer
        self.name = name if name else f"Node {int(time.time())}"
        self.node_data = {}  # Store form data
        
        # Connection tracking - store name of connected nodes
        self.input_connected_node = None   # Name of node connected to input, or None
        self.output_connected_node = None  # Name of node connected to output, or None
        
        # Double click detection
        self.last_click_time = 0
        self.double_click_threshold = 0.4  # 400ms
        
        self.circle_radius = 6
        center_y = h / 2
        self.input_circle = InputOutputCircle(-self.circle_radius - self.circle_radius,
                                             center_y - self.circle_radius,
                                             self.circle_radius*2,
                                             self.circle_radius*2,
                                             self,
                                             'input')
        self.input_circle.setZValue(2)  # Input/output circles on top

        self.output_circle = InputOutputCircle(w - self.circle_radius + self.circle_radius,
                                              center_y - self.circle_radius,
                                              self.circle_radius*2,
                                              self.circle_radius*2,
                                              self,
                                              'output')
        self.output_circle.setZValue(2)  # Input/output circles on top

    def mousePressEvent(self, event):
        # If click is on input/output circle, ignore so child gets event
        pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
        for circle in [self.input_circle, self.output_circle]:
            if circle.contains(circle.mapFromParent(pos)):
                event.ignore()
                return
                
        if event.button() == Qt.LeftButton:
            current_time = time.time()
            
            # Check for double click
            if (current_time - self.last_click_time) < self.double_click_threshold:
                # Double click detected - open form
                self.open_form()
                self.last_click_time = 0  # Reset to prevent triple click
                event.accept()
                return
            else:
                # Single click - start dragging
                self.last_click_time = current_time
                self._drag_start = event.pos()
                self.setCursor(Qt.ClosedHandCursor)
                event.accept()
        elif event.button() == Qt.RightButton:
            # Right click - show context menu
            self.show_context_menu(event.screenPos())
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        if hasattr(self, '_drag_start') and self._drag_start is not None:
            # Move node by mouse delta
            delta = event.pos() - self._drag_start
            self.setPos(self.pos() + delta)
            
            # Update connected edges
            self.updateConnectedEdges()
            
            # Update connection tracking to ensure data is current
            self.updateConnectionTracking()
            
            # --- Expand scene rect if node dragged out of bounds ---
            scene = self.scene()
            if scene:
                node_rect = self.sceneBoundingRect()
                scene_rect = scene.sceneRect()
                offset = 40
                node_rect = node_rect.adjusted(-offset, -offset, offset, offset)
                new_rect = scene_rect.united(node_rect)
                if new_rect != scene_rect:
                    scene.setSceneRect(new_rect)
            event.accept()
        else:
            event.ignore()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start = None
            self.setCursor(Qt.ArrowCursor)
            event.accept()
        else:
            event.ignore()

    def updateConnectedEdges(self):
        """Update all edges connected to this node's input/output circles"""
        for circle in [self.input_circle, self.output_circle]:
            if hasattr(circle, 'connected_edges'):
                for edge in circle.connected_edges:
                    edge.updateFromNodes()

    def updateConnectionTracking(self):
        """Update input_connected_node and output_connected_node based on current edges"""
        # Reset connections
        self.input_connected_node = None
        self.output_connected_node = None
        
        # Check input circle connections
        if hasattr(self.input_circle, 'connected_edges'):
            for edge in self.input_circle.connected_edges:
                if edge.start_circle == self.input_circle:
                    # This input is the start of the edge, find the end node
                    if edge.end_circle and hasattr(edge.end_circle, 'parentItem'):
                        parent_node = edge.end_circle.parentItem()
                        if isinstance(parent_node, (NodeScene, StartNode, BranchNode)):
                            self.input_connected_node = parent_node.name
                            break
                elif edge.end_circle == self.input_circle:
                    # This input is the end of the edge, find the start node
                    if edge.start_circle and hasattr(edge.start_circle, 'parentItem'):
                        parent_node = edge.start_circle.parentItem()
                        if isinstance(parent_node, (NodeScene, StartNode, BranchNode)):
                            self.input_connected_node = parent_node.name
                            break
        
        # Check output circle connections
        if hasattr(self.output_circle, 'connected_edges'):
            for edge in self.output_circle.connected_edges:
                if edge.start_circle == self.output_circle:
                    # This output is the start of the edge, find the end node
                    if edge.end_circle and hasattr(edge.end_circle, 'parentItem'):
                        parent_node = edge.end_circle.parentItem()
                        if isinstance(parent_node, (NodeScene, StartNode, BranchNode)):
                            self.output_connected_node = parent_node.name
                            break
                elif edge.end_circle == self.output_circle:
                    # This output is the end of the edge, find the start node
                    if edge.start_circle and hasattr(edge.start_circle, 'parentItem'):
                        parent_node = edge.start_circle.parentItem()
                        if isinstance(parent_node, (NodeScene, StartNode, BranchNode)):
                            self.output_connected_node = parent_node.name
                            break

    def show_context_menu(self, screen_pos):
        """Show context menu with Delete and Duplicate options"""
        menu = QMenu()
        
        # Add actions
        edit_action = menu.addAction("Edit")
        duplicate_action = menu.addAction("Duplicate")
        menu.addSeparator()
        delete_action = menu.addAction("Delete")
        
        # Execute menu and handle selection
        action = menu.exec(screen_pos)
        
        if action == edit_action:
            self.open_form()
        elif action == duplicate_action:
            self.duplicate_node()
        elif action == delete_action:
            self.delete_node()

    def duplicate_node(self):
        """Duplicate this node"""
        scene = self.scene()
        if not scene:
            return
        
        # Get main window for access to node_items list
        main_window = None
        for view in scene.views():
            main_window = view.window()
            break
        
        if main_window and hasattr(main_window, 'node_items'):
            # Create new node at offset position
            offset = 150
            new_x = self.pos().x() + offset
            new_y = self.pos().y() + offset
            
            # Create duplicate node
            new_node = NodeScene(new_x, new_y, self.rect().width(), self.rect().height(), 
                               f"{self.name}_copy")
            
            # Copy all node data
            if self.node_data:
                new_node.node_data = self.node_data.copy()
                # Update the name in the copied data
                new_node.node_data['name'] = new_node.name
            
            # Add to scene and node list
            scene.addItem(new_node)
            main_window.node_items.append(new_node)
            
            # Update scene rect to include new node
            node_rect = new_node.sceneBoundingRect()
            scene_rect = scene.sceneRect()
            offset_rect = 40
            node_rect = node_rect.adjusted(-offset_rect, -offset_rect, offset_rect, offset_rect)
            new_rect = scene_rect.united(node_rect)
            scene.setSceneRect(new_rect)
            
            # Show status message
            if hasattr(main_window, 'status_bar'):
                main_window.status_bar.showMessage(f"Duplicated node '{self.name}' as '{new_node.name}'", 3000)
            
            print(f"Duplicated node '{self.name}' as '{new_node.name}' at position ({new_x}, {new_y})")

    def delete_node(self):
        """Delete this node and clean up all connections"""
        scene = self.scene()
        if not scene:
            return
        
        # Get main window for access to node_items list
        main_window = None
        for view in scene.views():
            main_window = view.window()
            break
        
        # Remove all connected edges first
        edges_to_remove = []
        
        # Collect edges from input circle
        if hasattr(self.input_circle, 'connected_edges'):
            edges_to_remove.extend(self.input_circle.connected_edges[:])  # Make a copy
        
        # Collect edges from output circle
        if hasattr(self.output_circle, 'connected_edges'):
            edges_to_remove.extend(self.output_circle.connected_edges[:])  # Make a copy
        
        # Remove all collected edges
        for edge in edges_to_remove:
            edge.removeFromConnections()
            scene.removeItem(edge)
        
        # Remove node from main window's node list
        if main_window and hasattr(main_window, 'node_items'):
            if self in main_window.node_items:
                main_window.node_items.remove(self)
        
        # Remove node from scene
        scene.removeItem(self)
        
        # Show status message
        if main_window and hasattr(main_window, 'status_bar'):
            main_window.status_bar.showMessage(f"Deleted node '{self.name}'", 3000)
        
        print(f"Deleted node '{self.name}' and cleaned up all connections")

    def open_form(self):
        """Open form dialog to edit node data"""
        scene = self.scene()
        if scene and hasattr(scene, 'views') and scene.views():
            main_window = None
            for view in scene.views():
                main_window = view.window()
                break
            
            if main_window:
                form = MyForm(main_window)
                
                # Pre-populate form with existing data if any
                if self.node_data:
                    # Set basic fields including new scene fields
                    form.scene_type_combo.setCurrentText(self.node_data.get('scene_type', 'INT.'))
                    form.name_input.setText(self.node_data.get('name', self.name))
                    form.time_input.setText(self.node_data.get('time_description', ''))
                    
                    # Set transition fields
                    in_scene = self.node_data.get('in_scene', '')
                    if in_scene in ["FADE IN"]:
                        form.in_scene_combo.setCurrentText(in_scene)
                    else:
                        form.in_scene_combo.setCurrentText("None")
                        form.in_scene_text.setText(in_scene)
                        form.in_scene_text.setVisible(True)
                    
                    out_scene = self.node_data.get('out_scene', '')
                    if out_scene in ["CUT TO", "DISSOLVE TO", "FADE OUT"]:
                        form.out_scene_combo.setCurrentText(out_scene)
                    else:
                        form.out_scene_combo.setCurrentText("None")
                        form.out_scene_text.setText(out_scene)
                        form.out_scene_text.setVisible(True)
                    
                    form.bg_input.setText(self.node_data.get('background', ''))
                    
                    # Clear ALL existing rows first
                    form.clear_all_rows()
                    
                    # Now restore data from saved items in correct order using new unified system
                    if 'items' in self.node_data:
                        for item in self.node_data['items']:
                            # Add row with correct type using new unified system
                            form.add_row()
                            if form.rows:
                                last_row = form.rows[-1]
                                # Set type dropdown
                                if item['type'] == 'dialog':
                                    last_row['type_combo'].setCurrentText('Dialog')
                                    # Set dialog specific fields
                                    last_row['character'].setText(item.get('character', ''))
                                    last_row['parentheticals'].setText(item.get('parentheticals', ''))
                                    last_row['text'].setText(item.get('text', ''))
                                elif item['type'] == 'action':
                                    last_row['type_combo'].setCurrentText('Action')
                                    # Set action specific fields
                                    last_row['text'].setText(item.get('text', ''))
                                
                                # Trigger type change to show/hide appropriate fields for NodeScene
                                form.on_type_changed(last_row['widget'], last_row['type_combo'].currentText())
                    
                    # Update row numbers ONCE after restoring all data
                    form.update_row_numbers()
                    
                    # Resize form based on number of rows for NodeScene
                    total_rows = len(form.rows)
                    if total_rows > 4:  # If more than default 4 rows
                        base_height = 400  # Minimum height
                        row_height = 50    # Height per row
                        extra_rows = total_rows - 4
                        new_height = base_height + (extra_rows * row_height)
                        
                        # Limit maximum height to screen height - 100px
                        screen_height = main_window.screen().availableGeometry().height()
                        max_height = screen_height - 100
                        new_height = min(new_height, max_height)
                        
                        form.resize(form.width(), new_height)
                        print(f"Restored {total_rows} rows and resized form to: {form.width()}x{new_height}")
                else:
                    # No existing data - start with empty form (NodeScene)
                    form.name_input.setText(self.name)
                    form.update_row_numbers()
                
                # Show form and get result for NodeScene
                if form.exec() == QDialog.Accepted:
                    # Get data from form
                    data = form.get_form_data()
                    
                    # Store ALL form data in node
                    self.node_data = data
                    
                    # Update node name
                    if data['name']:
                        self.name = data['name']
                    
                    print(f"Saved complete form data to node '{self.name}':")
                    print(f"  Name: {data.get('name', 'None')}")
                    print(f"  In Scene: {data.get('in_scene', 'None')}")
                    print(f"  Out Scene: {data.get('out_scene', 'None')}")
                    print(f"  Background: {data.get('background', 'None')}")
                    print(f"  Total Items: {len(data.get('items', []))}")
                    print(f"  Dialogs: {len(data.get('dialogs', []))}")
                    print(f"  Actions: {len(data.get('actions', []))}")
                    
                    # Print connection information
                    print(f"  Input Connected to: {self.input_connected_node if self.input_connected_node else 'None'}")
                    print(f"  Output Connected to: {self.output_connected_node if self.output_connected_node else 'None'}")
                    
                    # Print detailed items
                    for item in data.get('items', []):
                        if item['type'] == 'dialog':
                            parentheticals = f" {item['parentheticals']}" if item.get('parentheticals') else ""
                            print(f"    {item['order']}. Dialog - {item['character']}{parentheticals}: {item['text']}")
                        else:
                            print(f"    {item['order']}. Action - {item['text']}")
                    
                    # Force redraw to show updated name
                    scene.update()
                    
                    print(f"Node data successfully stored. Total data size: {len(str(self.node_data))} characters")


class StartNode(QGraphicsRectItem):
    """Special start node that has no input circle - only output"""
    def __init__(self, x, y, w=120, h=60, name=None):
        # Initialize as QGraphicsRectItem
        super().__init__(0, 0, w, h)
        self.setPos(x, y)
        self.setBrush(QBrush(QColor(100, 255, 100)))  # Light green for start node
        self.setPen(QColor(0, 200, 0))  # Green border
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsRectItem.ItemIsFocusable, True)
        self.setAcceptHoverEvents(True)
        self.setZValue(0)  # Node at middle layer
        self.name = name if name else "Start"
        self.node_data = {}  # Store form data
        
        # Connection tracking - start node only has output
        self.input_connected_node = None   # Always None for start node
        self.output_connected_node = None  # Name of node connected to output, or None
        
        # Double click detection
        self.last_click_time = 0
        self.double_click_threshold = 0.4  # 400ms
        
        self.circle_radius = 6
        center_y = h / 2
        
        # NO INPUT CIRCLE for start node
        self.input_circle = None
        
        # Only output circle
        self.output_circle = InputOutputCircle(w - self.circle_radius + self.circle_radius,
                                              center_y - self.circle_radius,
                                              self.circle_radius*2,
                                              self.circle_radius*2,
                                              self,
                                              'output')
        self.output_circle.setZValue(2)  # Output circle on top

    def mousePressEvent(self, event):
        # Modified to only check output circle (no input circle)
        pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
        if self.output_circle and self.output_circle.contains(self.output_circle.mapFromParent(pos)):
            event.ignore()
            return
                
        if event.button() == Qt.LeftButton:
            current_time = time.time()
            
            # Check for double click
            if (current_time - self.last_click_time) < self.double_click_threshold:
                # Double click detected - open form
                self.open_form()
                self.last_click_time = 0  # Reset to prevent triple click
                event.accept()
                return
            else:
                # Single click - start dragging
                self.last_click_time = current_time
                self._drag_start = event.pos()
                self.setCursor(Qt.ClosedHandCursor)
                event.accept()
        elif event.button() == Qt.RightButton:
            # Right click - show context menu
            self.show_context_menu(event.screenPos())
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        if hasattr(self, '_drag_start') and self._drag_start is not None:
            # Move node by mouse delta
            delta = event.pos() - self._drag_start
            self.setPos(self.pos() + delta)
            
            # Update connected edges
            self.updateConnectedEdges()
            
            # Update connection tracking to ensure data is current
            self.updateConnectionTracking()
            
            # --- Expand scene rect if node dragged out of bounds ---
            scene = self.scene()
            if scene:
                node_rect = self.sceneBoundingRect()
                scene_rect = scene.sceneRect()
                offset = 40
                node_rect = node_rect.adjusted(-offset, -offset, offset, offset)
                new_rect = scene_rect.united(node_rect)
                if new_rect != scene_rect:
                    scene.setSceneRect(new_rect)
            event.accept()
        else:
            event.ignore()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start = None
            self.setCursor(Qt.ArrowCursor)
            event.accept()
        else:
            event.ignore()

    def updateConnectedEdges(self):
        """Update all edges connected to this node's output circle only"""
        if self.output_circle and hasattr(self.output_circle, 'connected_edges'):
            for edge in self.output_circle.connected_edges:
                edge.updateFromNodes()

    def updateConnectionTracking(self):
        """Update output_connected_node based on current edges (no input for start node)"""
        # Reset connections
        self.input_connected_node = None  # Always None for start node
        self.output_connected_node = None
        
        # Check output circle connections only
        if self.output_circle and hasattr(self.output_circle, 'connected_edges'):
            for edge in self.output_circle.connected_edges:
                if edge.start_circle == self.output_circle:
                    # This output is the start of the edge, find the end node
                    if edge.end_circle and hasattr(edge.end_circle, 'parentItem'):
                        parent_node = edge.end_circle.parentItem()
                        if isinstance(parent_node, (NodeScene, StartNode, BranchNode)):
                            self.output_connected_node = parent_node.name
                            break
                elif edge.end_circle == self.output_circle:
                    # This output is the end of the edge, find the start node
                    if edge.start_circle and hasattr(edge.start_circle, 'parentItem'):
                        parent_node = edge.start_circle.parentItem()
                        if isinstance(parent_node, (NodeScene, StartNode, BranchNode)):
                            self.output_connected_node = parent_node.name
                            break

    def show_context_menu(self, screen_pos):
        """Show context menu with Delete and Duplicate options"""
        menu = QMenu()
        
        # Add actions
        edit_action = menu.addAction("Edit")
        duplicate_action = menu.addAction("Duplicate")
        menu.addSeparator()
        delete_action = menu.addAction("Delete")
        
        # Execute menu and handle selection
        action = menu.exec(screen_pos)
        
        if action == edit_action:
            self.open_form()
        elif action == duplicate_action:
            self.duplicate_node()
        elif action == delete_action:
            self.delete_node()

    def duplicate_node(self):
        """Duplicate this start node"""
        scene = self.scene()
        if not scene:
            return
        
        # Get main window for access to node_items list
        main_window = None
        for view in scene.views():
            main_window = view.window()
            break
        
        if main_window and hasattr(main_window, 'node_items'):
            # Create new start node at offset position
            offset = 150
            new_x = self.pos().x() + offset
            new_y = self.pos().y() + offset
            
            # Create duplicate start node
            new_node = StartNode(new_x, new_y, self.rect().width(), self.rect().height(), 
                               f"{self.name}_copy")
            
            # Copy all node data
            if self.node_data:
                new_node.node_data = self.node_data.copy()
                # Update the name in the copied data
                new_node.node_data['name'] = new_node.name
            
            # Add to scene and node list
            scene.addItem(new_node)
            main_window.node_items.append(new_node)
            
            # Update scene rect to include new node
            node_rect = new_node.sceneBoundingRect()
            scene_rect = scene.sceneRect()
            offset_rect = 40
            node_rect = node_rect.adjusted(-offset_rect, -offset_rect, offset_rect, offset_rect)
            new_rect = scene_rect.united(node_rect)
            scene.setSceneRect(new_rect)
            
            # Show status message
            if hasattr(main_window, 'status_bar'):
                main_window.status_bar.showMessage(f"Duplicated start node '{self.name}' as '{new_node.name}'", 3000)
            
            print(f"Duplicated start node '{self.name}' as '{new_node.name}' at position ({new_x}, {new_y})")

    def delete_node(self):
        """Delete this node and clean up all connections"""
        scene = self.scene()
        if not scene:
            return
        
        # Get main window for access to node_items list
        main_window = None
        for view in scene.views():
            main_window = view.window()
            break
        
        # Remove all connected edges first
        edges_to_remove = []
        
        # Collect edges from output circle only (StartNode has no input)
        if hasattr(self.output_circle, 'connected_edges'):
            edges_to_remove.extend(self.output_circle.connected_edges[:])  # Make a copy
        
        # Remove all collected edges
        for edge in edges_to_remove:
            edge.removeFromConnections()
            scene.removeItem(edge)
        
        # Remove node from main window's node list
        if main_window and hasattr(main_window, 'node_items'):
            if self in main_window.node_items:
                main_window.node_items.remove(self)
        
        # Remove node from scene
        scene.removeItem(self)
        
        # Show status message
        if main_window and hasattr(main_window, 'status_bar'):
            main_window.status_bar.showMessage(f"Deleted start node '{self.name}'", 3000)
        
        print(f"Deleted start node '{self.name}' and cleaned up all connections")

    def open_form(self):
        """Open form dialog to edit node data (same as NodeScene but for StartNode)"""
        scene = self.scene()
        if scene and hasattr(scene, 'views') and scene.views():
            main_window = None
            for view in scene.views():
                main_window = view.window()
                break
            
            if main_window:
                form = MyForm(main_window)
                
                # Pre-populate form with existing data if any
                if self.node_data:
                    # Set basic fields including new scene fields
                    form.scene_type_combo.setCurrentText(self.node_data.get('scene_type', 'INT.'))
                    form.name_input.setText(self.node_data.get('name', self.name))
                    form.time_input.setText(self.node_data.get('time_description', ''))
                    
                    # Set transition fields
                    in_scene = self.node_data.get('in_scene', '')
                    if in_scene in ["FADE IN"]:
                        form.in_scene_combo.setCurrentText(in_scene)
                    else:
                        form.in_scene_combo.setCurrentText("None")
                        form.in_scene_text.setText(in_scene)
                        form.in_scene_text.setVisible(True)
                    
                    out_scene = self.node_data.get('out_scene', '')
                    if out_scene in ["CUT TO", "DISSOLVE TO", "FADE OUT"]:
                        form.out_scene_combo.setCurrentText(out_scene)
                    else:
                        form.out_scene_combo.setCurrentText("None")
                        form.out_scene_text.setText(out_scene)
                        form.out_scene_text.setVisible(True)
                    
                    form.bg_input.setText(self.node_data.get('background', ''))
                    
                    # Clear ALL existing rows first
                    form.clear_all_rows()
                    
                    # Now restore data from saved items in correct order using new unified system
                    if 'items' in self.node_data:
                        for item in self.node_data['items']:
                            # Add row with correct type using new unified system
                            form.add_row()
                            if form.rows:
                                last_row = form.rows[-1]
                                # Set type dropdown
                                if item['type'] == 'dialog':
                                    last_row['type_combo'].setCurrentText('Dialog')
                                    # Set dialog specific fields
                                    last_row['character'].setText(item.get('character', ''))
                                    last_row['parentheticals'].setText(item.get('parentheticals', ''))
                                    last_row['text'].setText(item.get('text', ''))
                                elif item['type'] == 'action':
                                    last_row['type_combo'].setCurrentText('Action')
                                    # Set action specific fields
                                    last_row['text'].setText(item.get('text', ''))
                                
                                # Trigger type change to show/hide appropriate fields for StartNode
                                form.on_type_changed(last_row['widget'], last_row['type_combo'].currentText())
                    
                    # Update row numbers ONCE after restoring all data for StartNode
                    form.update_row_numbers()
                    
                    # Resize form based on number of rows for StartNode
                    total_rows = len(form.rows)
                    if total_rows > 4:  # If more than default 4 rows
                        base_height = 400  # Minimum height
                        row_height = 50    # Height per row
                        extra_rows = total_rows - 4
                        new_height = base_height + (extra_rows * row_height)
                        
                        # Limit maximum height to screen height - 100px
                        screen_height = main_window.screen().availableGeometry().height()
                        max_height = screen_height - 100
                        new_height = min(new_height, max_height)
                        
                        form.resize(form.width(), new_height)
                        print(f"Restored {total_rows} rows and resized form to: {form.width()}x{new_height}")
                else:
                    # No existing data - start with empty form for StartNode
                    form.name_input.setText(self.name)
                    form.update_row_numbers()
                
                # Show form and get result
                if form.exec() == QDialog.Accepted:
                    # Get data from form
                    data = form.get_form_data()
                    
                    # Store ALL form data in node
                    self.node_data = data
                    
                    # Update node name
                    if data['name']:
                        self.name = data['name']
                    
                    print(f"Saved complete form data to StartNode '{self.name}':")
                    print(f"  Name: {data.get('name', 'None')}")
                    print(f"  In Scene: {data.get('in_scene', 'None')}")
                    print(f"  Out Scene: {data.get('out_scene', 'None')}")
                    print(f"  Background: {data.get('background', 'None')}")
                    print(f"  Total Items: {len(data.get('items', []))}")
                    print(f"  Dialogs: {len(data.get('dialogs', []))}")
                    print(f"  Actions: {len(data.get('actions', []))}")
                    
                    # Print connection information (StartNode has no input)
                    print(f"  Input Connected to: None (Start node has no input)")
                    print(f"  Output Connected to: {self.output_connected_node if self.output_connected_node else 'None'}")
                    
                    # Print detailed items
                    for item in data.get('items', []):
                        if item['type'] == 'dialog':
                            parentheticals = f" {item['parentheticals']}" if item.get('parentheticals') else ""
                            print(f"    {item['order']}. Dialog - {item['character']}{parentheticals}: {item['text']}")
                        else:
                            print(f"    {item['order']}. Action - {item['text']}")
                    
                    # Force redraw to show updated name
                    scene.update()
                    
                    print(f"StartNode data successfully stored. Total data size: {len(str(self.node_data))} characters")


class BranchNode(QGraphicsRectItem):
    """Special branch node that has one input and multiple outputs for branching storylines"""
    def __init__(self, x, y, w=140, h=None, name=None):
        # Calculate initial height based on default output count
        self.circle_radius = 6
        self.output_spacing = 25  # Fixed spacing between outputs
        self.top_bottom_margin = 20  # Margin from top and bottom
        
        # Calculate height for 1 output
        initial_outputs = 1
        calculated_h = self.calculate_height_for_outputs(initial_outputs)
        h = h if h else calculated_h
        
        # Initialize as QGraphicsRectItem
        super().__init__(0, 0, w, h)
        self.setPos(x, y)
        self.setBrush(QBrush(QColor(255, 200, 100)))  # Light orange for branch node
        self.setPen(QColor(200, 150, 0))  # Orange border
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsRectItem.ItemIsFocusable, True)
        self.setAcceptHoverEvents(True)
        self.setZValue(0)  # Node at middle layer
        self.name = name if name else f"Branch {int(time.time())}"
        self.node_data = {}  # Store form data
        
        # Connection tracking - branch node has one input and multiple outputs
        self.input_connected_node = None   # Name of node connected to input, or None
        self.output_connected_nodes = []   # List of node names connected to outputs
        
        # Double click detection
        self.last_click_time = 0
        self.double_click_threshold = 0.4  # 400ms
        
        w = self.rect().width()
        h = self.rect().height()
        center_y = h / 2
        
        # Input circle (left side, center)
        self.input_circle = InputOutputCircle(-self.circle_radius - self.circle_radius,
                                             center_y - self.circle_radius,
                                             self.circle_radius*2,
                                             self.circle_radius*2,
                                             self,
                                             'input')
        self.input_circle.setZValue(2)  # Input circle on top

        # Create initial output circles
        self.output_circles = []
        self.create_output_circles(initial_outputs)

    def calculate_height_for_outputs(self, num_outputs):
        """Calculate required height for given number of outputs"""
        if num_outputs <= 0:
            num_outputs = 1
        total_output_height = (num_outputs - 1) * self.output_spacing
        return total_output_height + (2 * self.top_bottom_margin)

    def create_output_circles(self, num_outputs):
        """Create output circles positioned from center"""
        w = self.rect().width()
        h = self.rect().height()
        center_y = h / 2
        
        # Clear existing circles
        for circle in self.output_circles:
            if circle.scene():
                circle.scene().removeItem(circle)
        self.output_circles = []
        
        # Calculate starting position (center for odd numbers, between center for even)
        if num_outputs == 1:
            # Single output at center
            positions = [center_y]
        else:
            # Multiple outputs centered around middle
            total_height = (num_outputs - 1) * self.output_spacing
            start_y = center_y - (total_height / 2)
            positions = [start_y + (i * self.output_spacing) for i in range(num_outputs)]
        
        # Create output circles
        for i, y_pos in enumerate(positions):
            output_circle = InputOutputCircle(w - self.circle_radius + self.circle_radius,
                                            y_pos - self.circle_radius,
                                            self.circle_radius*2,
                                            self.circle_radius*2,
                                            self,
                                            'output')
            output_circle.setZValue(2)
            self.output_circles.append(output_circle)

    def resize_node_for_outputs(self, num_outputs):
        """Resize the node to accommodate the number of outputs"""
        w = self.rect().width()
        new_h = self.calculate_height_for_outputs(num_outputs)
        
        # Update the rectangle
        self.setRect(0, 0, w, new_h)
        
        # Reposition input circle to new center - use setRect instead of setPos
        center_y = new_h / 2
        input_x = -self.circle_radius - self.circle_radius
        input_y = center_y - self.circle_radius
        self.input_circle.setRect(input_x, input_y, self.circle_radius*2, self.circle_radius*2)
        
        # Update connected edges for input circle immediately
        if hasattr(self.input_circle, 'connected_edges'):
            for edge in self.input_circle.connected_edges:
                if hasattr(edge, 'updateFromNodes'):
                    edge.updateFromNodes()
        
        # Recreate output circles with new positioning
        self.create_output_circles(num_outputs)
        
        # Update all connected edges for output circles
        for circle in self.output_circles:
            if hasattr(circle, 'connected_edges'):
                for edge in circle.connected_edges:
                    if hasattr(edge, 'updateFromNodes'):
                        edge.updateFromNodes()
        
        # Force scene update
        if self.scene():
            self.scene().update()

    def mousePressEvent(self, event):
        # Check if click is on input/output circles, ignore so child gets event
        pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
        
        # Check input circle
        if self.input_circle and self.input_circle.contains(self.input_circle.mapFromParent(pos)):
            event.ignore()
            return
        
        # Check all output circles
        for circle in self.output_circles:
            if circle and circle.contains(circle.mapFromParent(pos)):
                event.ignore()
                return
                
        if event.button() == Qt.LeftButton:
            current_time = time.time()
            
            # Check for double click
            if (current_time - self.last_click_time) < self.double_click_threshold:
                # Double click detected - open form
                self.open_form()
                self.last_click_time = 0  # Reset to prevent triple click
                event.accept()
                return
            else:
                # Single click - start dragging
                self.last_click_time = current_time
                self._drag_start = event.pos()
                self.setCursor(Qt.ClosedHandCursor)
                event.accept()
        elif event.button() == Qt.RightButton:
            # Right click - show context menu
            self.show_context_menu(event.screenPos())
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        if hasattr(self, '_drag_start') and self._drag_start is not None:
            # Move node by mouse delta
            delta = event.pos() - self._drag_start
            self.setPos(self.pos() + delta)
            
            # Update connected edges
            self.updateConnectedEdges()
            
            # Update connection tracking to ensure data is current
            self.updateConnectionTracking()
            
            # --- Expand scene rect if node dragged out of bounds ---
            scene = self.scene()
            if scene:
                node_rect = self.sceneBoundingRect()
                scene_rect = scene.sceneRect()
                offset = 40
                node_rect = node_rect.adjusted(-offset, -offset, offset, offset)
                new_rect = scene_rect.united(node_rect)
                if new_rect != scene_rect:
                    scene.setSceneRect(new_rect)
            event.accept()
        else:
            event.ignore()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start = None
            self.setCursor(Qt.ArrowCursor)
            event.accept()
        else:
            event.ignore()

    def updateConnectedEdges(self):
        """Update all edges connected to this node's input/output circles"""
        # Update input circle
        if self.input_circle and hasattr(self.input_circle, 'connected_edges'):
            for edge in self.input_circle.connected_edges:
                edge.updateFromNodes()
        
        # Update all output circles
        for circle in self.output_circles:
            if hasattr(circle, 'connected_edges'):
                for edge in circle.connected_edges:
                    edge.updateFromNodes()

    def updateConnectionTracking(self):
        """Update input_connected_node and output_connected_nodes based on current edges"""
        # Reset connections
        self.input_connected_node = None
        self.output_connected_nodes = []
        
        # Check input circle connections
        if self.input_circle and hasattr(self.input_circle, 'connected_edges'):
            for edge in self.input_circle.connected_edges:
                if edge.start_circle == self.input_circle:
                    # This input is the start of the edge, find the end node
                    if edge.end_circle and hasattr(edge.end_circle, 'parentItem'):
                        parent_node = edge.end_circle.parentItem()
                        if isinstance(parent_node, (NodeScene, StartNode, BranchNode)):
                            self.input_connected_node = parent_node.name
                            break
                elif edge.end_circle == self.input_circle:
                    # This input is the end of the edge, find the start node
                    if edge.start_circle and hasattr(edge.start_circle, 'parentItem'):
                        parent_node = edge.start_circle.parentItem()
                        if isinstance(parent_node, (NodeScene, StartNode, BranchNode)):
                            self.input_connected_node = parent_node.name
                            break
        
        # Check all output circles connections
        for circle in self.output_circles:
            if hasattr(circle, 'connected_edges'):
                for edge in circle.connected_edges:
                    if edge.start_circle == circle:
                        # This output is the start of the edge, find the end node
                        if edge.end_circle and hasattr(edge.end_circle, 'parentItem'):
                            parent_node = edge.end_circle.parentItem()
                            if isinstance(parent_node, (NodeScene, StartNode, BranchNode)):
                                if parent_node.name not in self.output_connected_nodes:
                                    self.output_connected_nodes.append(parent_node.name)
                    elif edge.end_circle == circle:
                        # This output is the end of the edge, find the start node
                        if edge.start_circle and hasattr(edge.start_circle, 'parentItem'):
                            parent_node = edge.start_circle.parentItem()
                            if isinstance(parent_node, (NodeScene, StartNode, BranchNode)):
                                if parent_node.name not in self.output_connected_nodes:
                                    self.output_connected_nodes.append(parent_node.name)

    def show_context_menu(self, screen_pos):
        """Show context menu with Edit, Add/Remove Output, and Delete options"""
        menu = QMenu()
        
        # Add actions
        edit_action = menu.addAction("Edit")
        duplicate_action = menu.addAction("Duplicate")
        menu.addSeparator()
        
        # Add output management options
        add_output_action = menu.addAction("➕ Add Output")
        remove_output_action = menu.addAction("➖ Remove Output")
        
        # Disable remove output if only one output exists
        if len(self.output_circles) <= 1:
            remove_output_action.setEnabled(False)
        
        # Disable add output if maximum outputs reached
        if len(self.output_circles) >= 8:
            add_output_action.setEnabled(False)
        
        menu.addSeparator()
        delete_action = menu.addAction("Delete")
        
        # Execute menu and handle selection
        action = menu.exec(screen_pos)
        
        if action == edit_action:
            self.open_form()
        elif action == duplicate_action:
            self.duplicate_node()
        elif action == add_output_action:
            self.add_output_circle()
        elif action == remove_output_action:
            self.remove_output_circle()
        elif action == delete_action:
            self.delete_node()

    def add_output_circle(self):
        """Add a new output circle to the branch node"""
        if len(self.output_circles) >= 8:
            return  # Maximum 8 outputs
        
        current_count = len(self.output_circles)
        new_count = current_count + 1
        
        # Store connections before resizing
        connections = []
        for i, circle in enumerate(self.output_circles):
            if hasattr(circle, 'connected_edges'):
                for edge in circle.connected_edges:
                    connections.append((i, edge))
        
        # Store input connections separately
        input_connections = []
        if hasattr(self.input_circle, 'connected_edges'):
            input_connections = self.input_circle.connected_edges[:]
        
        # Resize node and recreate circles
        self.resize_node_for_outputs(new_count)
        
        # Restore input connections
        if input_connections:
            if not hasattr(self.input_circle, 'connected_edges'):
                self.input_circle.connected_edges = []
            self.input_circle.connected_edges = input_connections
            
            # Update input edges
            for edge in input_connections:
                if hasattr(edge, 'updateFromNodes'):
                    edge.updateFromNodes()
        
        # Restore output connections
        for original_index, edge in connections:
            if original_index < len(self.output_circles):
                circle = self.output_circles[original_index]
                if not hasattr(circle, 'connected_edges'):
                    circle.connected_edges = []
                circle.connected_edges.append(edge)
                
                # Update edge references
                if edge.start_circle in self.output_circles or edge.end_circle in self.output_circles:
                    edge.updateFromNodes()
        
        print(f"Added output. Total: {len(self.output_circles)}")
        
        # Update scene
        if self.scene():
            self.scene().update()
            
        # Show status message
        scene = self.scene()
        if scene:
            for view in scene.views():
                main_window = view.window()
                if main_window and hasattr(main_window, 'status_bar'):
                    main_window.status_bar.showMessage(f"Added output (Total: {len(self.output_circles)})", 2000)
                break

    def remove_output_circle(self):
        """Remove the last output circle from the branch node"""
        if len(self.output_circles) <= 1:
            return  # Keep at least one output
        
        current_count = len(self.output_circles)
        new_count = current_count - 1
        
        # Store connections from remaining circles (excluding the last one)
        connections = []
        for i in range(new_count):  # Only save connections for remaining circles
            circle = self.output_circles[i]
            if hasattr(circle, 'connected_edges'):
                for edge in circle.connected_edges:
                    connections.append((i, edge))
        
        # Store input connections separately
        input_connections = []
        if hasattr(self.input_circle, 'connected_edges'):
            input_connections = self.input_circle.connected_edges[:]
        
        # Remove connections from the last circle
        last_circle = self.output_circles[-1]
        if hasattr(last_circle, 'connected_edges'):
            for edge in last_circle.connected_edges[:]:
                edge.removeFromConnections()
                if edge.scene():
                    edge.scene().removeItem(edge)
        
        # Resize node and recreate circles
        self.resize_node_for_outputs(new_count)
        
        # Restore input connections
        if input_connections:
            if not hasattr(self.input_circle, 'connected_edges'):
                self.input_circle.connected_edges = []
            self.input_circle.connected_edges = input_connections
            
            # Update input edges
            for edge in input_connections:
                if hasattr(edge, 'updateFromNodes'):
                    edge.updateFromNodes()
        
        # Restore connections for remaining circles
        for original_index, edge in connections:
            if original_index < len(self.output_circles):
                circle = self.output_circles[original_index]
                if not hasattr(circle, 'connected_edges'):
                    circle.connected_edges = []
                circle.connected_edges.append(edge)
                
                # Update edge references
                if edge.start_circle in self.output_circles or edge.end_circle in self.output_circles:
                    edge.updateFromNodes()
        
        print(f"Removed output. Total: {len(self.output_circles)}")
        
        # Update scene
        if self.scene():
            self.scene().update()
            
        # Show status message
        scene = self.scene()
        if scene:
            for view in scene.views():
                main_window = view.window()
                if main_window and hasattr(main_window, 'status_bar'):
                    main_window.status_bar.showMessage(f"Removed output (Total: {len(self.output_circles)})", 2000)
                break

    def duplicate_node(self):
        """Duplicate this branch node"""
        scene = self.scene()
        if not scene:
            return
        
        # Get main window for access to node_items list
        main_window = None
        for view in scene.views():
            main_window = view.window()
            break
        
        if main_window and hasattr(main_window, 'node_items'):
            # Create new branch node at offset position
            offset = 150
            new_x = self.pos().x() + offset
            new_y = self.pos().y() + offset
            
            # Create duplicate branch node
            new_node = BranchNode(new_x, new_y, self.rect().width(), self.rect().height(), 
                                f"{self.name}_copy")
            
            # Set same number of outputs as original
            while len(new_node.output_circles) < len(self.output_circles):
                new_node.add_output_circle()
            while len(new_node.output_circles) > len(self.output_circles):
                new_node.remove_output_circle()
            
            # Copy all node data
            if self.node_data:
                new_node.node_data = self.node_data.copy()
                # Update the name in the copied data
                new_node.node_data['name'] = new_node.name
            
            # Add to scene and node list
            scene.addItem(new_node)
            main_window.node_items.append(new_node)
            
            # Update scene rect to include new node
            node_rect = new_node.sceneBoundingRect()
            scene_rect = scene.sceneRect()
            offset_rect = 40
            node_rect = node_rect.adjusted(-offset_rect, -offset_rect, offset_rect, offset_rect)
            new_rect = scene_rect.united(node_rect)
            scene.setSceneRect(new_rect)
            
            # Show status message
            if hasattr(main_window, 'status_bar'):
                main_window.status_bar.showMessage(f"Duplicated branch node '{self.name}' as '{new_node.name}'", 3000)
            
            print(f"Duplicated branch node '{self.name}' as '{new_node.name}' at position ({new_x}, {new_y})")

    def delete_node(self):
        """Delete this node and clean up all connections"""
        scene = self.scene()
        if not scene:
            return
        
        # Get main window for access to node_items list
        main_window = None
        for view in scene.views():
            main_window = view.window()
            break
        
        # Remove all connected edges first
        edges_to_remove = []
        
        # Collect edges from input circle
        if self.input_circle and hasattr(self.input_circle, 'connected_edges'):
            edges_to_remove.extend(self.input_circle.connected_edges[:])  # Make a copy
        
        # Collect edges from all output circles
        for circle in self.output_circles:
            if hasattr(circle, 'connected_edges'):
                edges_to_remove.extend(circle.connected_edges[:])  # Make a copy
        
        # Remove all collected edges
        for edge in edges_to_remove:
            edge.removeFromConnections()
            scene.removeItem(edge)
        
        # Remove node from main window's node list
        if main_window and hasattr(main_window, 'node_items'):
            if self in main_window.node_items:
                main_window.node_items.remove(self)
        
        # Remove node from scene
        scene.removeItem(self)
        
        # Show status message
        if main_window and hasattr(main_window, 'status_bar'):
            main_window.status_bar.showMessage(f"Deleted branch node '{self.name}'", 3000)
        
        print(f"Deleted branch node '{self.name}' and cleaned up all connections")

    def open_form(self):
        """Open form dialog to edit branch node data (same as NodeScene but for BranchNode)"""
        scene = self.scene()
        if scene and hasattr(scene, 'views') and scene.views():
            main_window = None
            for view in scene.views():
                main_window = view.window()
                break
            
            if main_window:
                form = MyForm(main_window)
                
                # Pre-populate form with existing data if any
                if self.node_data:
                    # Set basic fields including new scene fields
                    form.scene_type_combo.setCurrentText(self.node_data.get('scene_type', 'INT.'))
                    form.name_input.setText(self.node_data.get('name', self.name))
                    form.time_input.setText(self.node_data.get('time_description', ''))
                    
                    # Set transition fields
                    in_scene = self.node_data.get('in_scene', '')
                    if in_scene in ["FADE IN"]:
                        form.in_scene_combo.setCurrentText(in_scene)
                    else:
                        form.in_scene_combo.setCurrentText("None")
                        form.in_scene_text.setText(in_scene)
                        form.in_scene_text.setVisible(True)
                    
                    out_scene = self.node_data.get('out_scene', '')
                    if out_scene in ["CUT TO", "DISSOLVE TO", "FADE OUT"]:
                        form.out_scene_combo.setCurrentText(out_scene)
                    else:
                        form.out_scene_combo.setCurrentText("None")
                        form.out_scene_text.setText(out_scene)
                        form.out_scene_text.setVisible(True)
                    
                    form.bg_input.setText(self.node_data.get('background', ''))
                    
                    # Clear ALL existing rows first
                    form.clear_all_rows()
                    
                    # Now restore data from saved items in correct order using new unified system
                    if 'items' in self.node_data:
                        for item in self.node_data['items']:
                            # Add row with correct type using new unified system
                            form.add_row()
                            if form.rows:
                                last_row = form.rows[-1]
                                # Set type dropdown
                                if item['type'] == 'dialog':
                                    last_row['type_combo'].setCurrentText('Dialog')
                                    # Set dialog specific fields
                                    last_row['character'].setText(item.get('character', ''))
                                    last_row['parentheticals'].setText(item.get('parentheticals', ''))
                                    last_row['text'].setText(item.get('text', ''))
                                elif item['type'] == 'action':
                                    last_row['type_combo'].setCurrentText('Action')
                                    # Set action specific fields
                                    last_row['text'].setText(item.get('text', ''))
                                
                                # Trigger type change to show/hide appropriate fields for BranchNode
                                form.on_type_changed(last_row['widget'], last_row['type_combo'].currentText())
                    
                    # Update row numbers ONCE after restoring all data for BranchNode
                    form.update_row_numbers()
                    
                    # Resize form based on number of rows for BranchNode
                    total_rows = len(form.rows)
                    if total_rows > 4:  # If more than default 4 rows
                        base_height = 400  # Minimum height
                        row_height = 50    # Height per row
                        extra_rows = total_rows - 4
                        new_height = base_height + (extra_rows * row_height)
                        
                        # Limit maximum height to screen height - 100px
                        screen_height = main_window.screen().availableGeometry().height()
                        max_height = screen_height - 100
                        new_height = min(new_height, max_height)
                        
                        form.resize(form.width(), new_height)
                        print(f"Restored {total_rows} rows and resized form to: {form.width()}x{new_height}")
                else:
                    # No existing data - start with empty form for BranchNode
                    form.name_input.setText(self.name)
                    form.update_row_numbers()
                
                # Show form and get result
                if form.exec() == QDialog.Accepted:
                    # Get data from form
                    data = form.get_form_data()
                    
                    # Store ALL form data in node
                    self.node_data = data
                    
                    # Update node name
                    if data['name']:
                        self.name = data['name']
                    
                    print(f"Saved complete form data to BranchNode '{self.name}':")
                    print(f"  Name: {data.get('name', 'None')}")
                    print(f"  In Scene: {data.get('in_scene', 'None')}")
                    print(f"  Out Scene: {data.get('out_scene', 'None')}")
                    print(f"  Background: {data.get('background', 'None')}")
                    print(f"  Total Items: {len(data.get('items', []))}")
                    print(f"  Dialogs: {len(data.get('dialogs', []))}")
                    print(f"  Actions: {len(data.get('actions', []))}")
                    
                    # Print connection information for BranchNode
                    print(f"  Input Connected to: {self.input_connected_node if self.input_connected_node else 'None'}")
                    print(f"  Outputs Connected to: {', '.join(self.output_connected_nodes) if self.output_connected_nodes else 'None'}")
                    print(f"  Total Output Connections: {len(self.output_connected_nodes)}")
                    
                    # Print detailed items
                    for item in data.get('items', []):
                        if item['type'] == 'dialog':
                            parentheticals = f" {item['parentheticals']}" if item.get('parentheticals') else ""
                            print(f"    {item['order']}. Dialog - {item['character']}{parentheticals}: {item['text']}")
                        else:
                            print(f"    {item['order']}. Action - {item['text']}")
                    
                    # Force redraw to show updated name
                    scene.update()
                    
                    print(f"BranchNode data successfully stored. Total data size: {len(str(self.node_data))} characters")
