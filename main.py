from PySide6.QtWidgets import QGraphicsEllipseItem
from PySide6.QtWidgets import QGraphicsPathItem
from PySide6.QtGui import QPainterPath, QPen, QColor
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QDialog, QMenuBar, QMenu, QFileDialog, QMessageBox
from PySide6.QtCore import Qt, QPointF, QTimer
from PySide6.QtGui import QAction
import time
import json
import os
import csv

# PDF generation imports
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem
from PySide6.QtGui import QMouseEvent, QBrush, QColor
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsScene
from PySide6.QtCore import QEvent, QRectF


# Import form from parent directory
import sys
import os
# Import form from local module
from form import MyForm


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
                    if isinstance(self_node, (NodeScene, StartNode)):
                        self_node.updateConnectionTracking()
                    if isinstance(target_node, (NodeScene, StartNode)):
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
            if isinstance(self_node, (NodeScene, StartNode)):
                self_node.updateConnectionTracking()
            if isinstance(new_node, (NodeScene, StartNode)):
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
            if isinstance(start_node, (NodeScene, StartNode)):
                start_node.updateConnectionTracking()
        if self.end_circle:
            end_node = self.end_circle.parentItem()
            if isinstance(end_node, (NodeScene, StartNode)):
                end_node.updateConnectionTracking()
from PySide6.QtWidgets import QGraphicsView

class NodeGraphicsView(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._zoom = 1.0
        self._zoom_step = 1.15
        self._zoom_min = 0.2
        self._zoom_max = 5.0

    def wheelEvent(self, event):
        # Zoom in/out with mouse wheel
        angle = event.angleDelta().y()
        factor = self._zoom_step if angle > 0 else 1 / self._zoom_step
        new_zoom = self._zoom * factor
        if self._zoom_min <= new_zoom <= self._zoom_max:
            self._zoom = new_zoom
            self.scale(factor, factor)
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete or event.key() == Qt.Key_Backspace:
            # Delete selected edges (Delete key for Windows/Linux, Backspace for Mac)
            selected_items = self.scene().selectedItems()
            for item in selected_items:
                if isinstance(item, EdgeGraphicsItem):
                    # Remove from connections before deleting
                    item.removeFromConnections()
                    self.scene().removeItem(item)
            event.accept()
        else:
            super().keyPressEvent(event)

    def drawForeground(self, painter, rect):
        """Draw node names on top of everything"""
        from PySide6.QtGui import QFont
        
        # Set font for node names
        font = QFont("Arial", 10)
        painter.setFont(font)
        painter.setPen(QColor(0, 0, 0))
        
        # Draw names for all nodes
        for item in self.scene().items():
            if isinstance(item, (NodeScene, StartNode)):
                # Calculate text position (center of node)
                node_rect = item.sceneBoundingRect()
                text_rect = node_rect.adjusted(5, 5, -5, -5)
                
                # Use different color for start node
                if isinstance(item, StartNode):
                    painter.setPen(QColor(0, 100, 0))  # Dark green for start node
                else:
                    painter.setPen(QColor(0, 0, 0))    # Black for regular nodes
                
                # Draw node name
                painter.drawText(text_rect, Qt.AlignCenter, item.name)
        
        super().drawForeground(painter, rect)

class NodeScene(QGraphicsRectItem):
    def input_mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            scene = self.scene()
            if scene:
                start_pos = self.input_circle.mapToScene(self.input_circle.rect().center())
                self._drag_edge = EdgeGraphicsItem(start_pos, start_pos)
                scene.addItem(self._drag_edge)
                self._drag_edge_active = 'input'
            event.accept()
        else:
            event.ignore()

    def output_mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            scene = self.scene()
            if scene:
                start_pos = self.output_circle.mapToScene(self.output_circle.rect().center())
                self._drag_edge = EdgeGraphicsItem(start_pos, start_pos)
                scene.addItem(self._drag_edge)
                self._drag_edge_active = 'output'
            event.accept()
        else:
            event.ignore()
            

    def mouseMoveEvent(self, event):
        if hasattr(self, '_drag_start') and self._drag_start is not None:
            # ...existing code...
            event.accept()
        elif hasattr(self, '_drag_edge') and self._drag_edge is not None:
            # Dragging edge
            scene = self.scene()
            if scene:
                # Always use event.pos() (QPoint) for mapToScene
                mouse_scene_pos = scene.views()[0].mapToScene(event.pos())
                self._drag_edge.setEndPos(mouse_scene_pos)
            event.accept()
        else:
            event.ignore()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start = None
            self.setCursor(Qt.ArrowCursor)
            # Remove edge if dragging
            if hasattr(self, '_drag_edge') and self._drag_edge is not None:
                scene = self.scene()
                if scene:
                    scene.removeItem(self._drag_edge)
                self._drag_edge = None
                self._drag_edge_active = None
            event.accept()
        else:
            event.ignore()
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
        else:
            event.ignore()  # ส่ง event ต่อไปเพื่อให้ canvas สามารถ panning ได้
    
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
                        if isinstance(parent_node, (NodeScene, StartNode)):
                            self.input_connected_node = parent_node.name
                            break
                elif edge.end_circle == self.input_circle:
                    # This input is the end of the edge, find the start node
                    if edge.start_circle and hasattr(edge.start_circle, 'parentItem'):
                        parent_node = edge.start_circle.parentItem()
                        if isinstance(parent_node, (NodeScene, StartNode)):
                            self.input_connected_node = parent_node.name
                            break
        
        # Check output circle connections
        if hasattr(self.output_circle, 'connected_edges'):
            for edge in self.output_circle.connected_edges:
                if edge.start_circle == self.output_circle:
                    # This output is the start of the edge, find the end node
                    if edge.end_circle and hasattr(edge.end_circle, 'parentItem'):
                        parent_node = edge.end_circle.parentItem()
                        if isinstance(parent_node, (NodeScene, StartNode)):
                            self.output_connected_node = parent_node.name
                            break
                elif edge.end_circle == self.output_circle:
                    # This output is the end of the edge, find the start node
                    if edge.start_circle and hasattr(edge.start_circle, 'parentItem'):
                        parent_node = edge.start_circle.parentItem()
                        if isinstance(parent_node, (NodeScene, StartNode)):
                            self.output_connected_node = parent_node.name
                            break

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start = None
            self.setCursor(Qt.ArrowCursor)
            event.accept()
        else:
            event.ignore()
    def __init__(self, x, y, w=120, h=60, name=None):
        super().__init__(0, 0, w, h)
        self.setPos(x, y)
        self.setBrush(QBrush(QColor(200, 200, 200)))
        self.setPen(QColor(0, 255, 0))
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, False)
        self.setAcceptHoverEvents(False)
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

#
# ใน MainWindow ใช้ NodeScene แทน QGraphicsScene
# และใน eventFilter ให้เรียก self.scene.add_node(x, y)

class StartNode(QGraphicsRectItem):
    """Special start node that has no input circle - only output"""
    def __init__(self, x, y, w=120, h=60, name=None):
        # Initialize as QGraphicsRectItem
        super().__init__(0, 0, w, h)
        self.setPos(x, y)
        self.setBrush(QBrush(QColor(100, 255, 100)))  # Light green for start node
        self.setPen(QColor(0, 200, 0))  # Green border
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, False)
        self.setAcceptHoverEvents(False)
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
                        if isinstance(parent_node, (NodeScene, StartNode)):
                            self.output_connected_node = parent_node.name
                            break
                elif edge.end_circle == self.output_circle:
                    # This output is the end of the edge, find the start node
                    if edge.start_circle and hasattr(edge.start_circle, 'parentItem'):
                        parent_node = edge.start_circle.parentItem()
                        if isinstance(parent_node, (NodeScene, StartNode)):
                            self.output_connected_node = parent_node.name
                            break

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
                            print(f"    {item['order']}. Dialog - {item['character']}: {item['text']}")
                        else:
                            print(f"    {item['order']}. Action - {item['text']}")
                    
                    # Force redraw to show updated name
                    scene.update()
                    
                    print(f"StartNode data successfully stored. Total data size: {len(str(self.node_data))} characters")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visual Novel Node")
        self.showMaximized()
        self.setMinimumSize(800, 600)
        self.setWindowState(Qt.WindowMaximized)
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

        self.scene = QGraphicsScene()
        self.view = NodeGraphicsView(self.scene)
        self.setCentralWidget(self.view)
        self.scene.setSceneRect(0, 0, self.width(), self.height())
        
        # Enable focus for key events
        self.view.setFocusPolicy(Qt.StrongFocus)

        self.node_items = []  # เก็บ NodeRectItem ทั้งหมด

        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)
        self._dragging = False
        self._drag_start = None

        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready - Right-click to create nodes, double-click to edit")
        
        # Update status bar periodically
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(2000)  # Update every 2 seconds

        # Menu bar actions
        self.initMenuBar()
        
        # Create default start node
        self.create_default_start_node()

    def initMenuBar(self):
        # Create menu bar
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        # File menu
        file_menu = QMenu("File", self)
        menu_bar.addMenu(file_menu)

        # New action
        new_action = QAction("New Graph", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_graph)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()

        # Load action
        load_action = QAction("Load Graph...", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.import_json)
        file_menu.addAction(load_action)

        # Save action
        save_action = QAction("Save Graph...", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.export_json)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # Export submenu
        export_menu = QMenu("Export Data", self)
        file_menu.addMenu(export_menu)
        
        # Export connected nodes as text
        export_text_action = QAction("Export as Text...", self)
        export_text_action.triggered.connect(self.export_connected_nodes_text)
        export_menu.addAction(export_text_action)
        
        # Export connected nodes as JSON
        export_json_action = QAction("Export Node Data as JSON...", self)
        export_json_action.triggered.connect(self.export_connected_nodes_json)
        export_menu.addAction(export_json_action)
        
        # Export as CSV
        export_csv_action = QAction("Export as CSV...", self)
        export_csv_action.triggered.connect(self.export_connected_nodes_csv)
        export_menu.addAction(export_csv_action)
        
        # Export as PDF
        export_pdf_action = QAction("Export as PDF Screenplay...", self)
        export_pdf_action.triggered.connect(self.export_connected_nodes_pdf)
        export_menu.addAction(export_pdf_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = QMenu("View", self)
        menu_bar.addMenu(view_menu)
        
        # Zoom actions
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut("Ctrl+=")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        zoom_reset_action = QAction("Reset Zoom", self)
        zoom_reset_action.setShortcut("Ctrl+0")
        zoom_reset_action.triggered.connect(self.zoom_reset)
        view_menu.addAction(zoom_reset_action)

        # Help menu
        help_menu = QMenu("Help", self)
        menu_bar.addMenu(help_menu)

        # Controls help action
        controls_action = QAction("Controls", self)
        controls_action.triggered.connect(self.show_controls)
        help_menu.addAction(controls_action)

        # About action
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def new_graph(self):
        """Create a new empty graph"""
        reply = QMessageBox.question(self, "New Graph", 
                                   "Create a new graph? This will clear all current nodes and edges.",
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.scene.clear()
            self.node_items.clear()
            # Reset scene to default size
            self.scene.setSceneRect(0, 0, self.width(), self.height())
            # Create new default start node
            self.create_default_start_node()

    def zoom_in(self):
        """Zoom in the view"""
        if hasattr(self.view, '_zoom') and self.view._zoom < self.view._zoom_max:
            factor = self.view._zoom_step
            self.view._zoom *= factor
            self.view.scale(factor, factor)

    def zoom_out(self):
        """Zoom out the view"""
        if hasattr(self.view, '_zoom') and self.view._zoom > self.view._zoom_min:
            factor = 1 / self.view._zoom_step
            self.view._zoom *= factor
            self.view.scale(factor, factor)

    def zoom_reset(self):
        """Reset zoom to 100%"""
        if hasattr(self.view, '_zoom'):
            current_zoom = self.view._zoom
            factor = 1 / current_zoom
            self.view._zoom = 1.0
            self.view.scale(factor, factor)

    def show_controls(self):
        """Show controls help dialog"""
        controls_text = """
<h3>Node Editor Controls</h3>
<p><b>Mouse Controls:</b></p>
<ul>
<li><b>Right Click (empty area):</b> Create new node</li>
<li><b>Double Click (node):</b> Open node form editor</li>
<li><b>Left Click + Drag (node):</b> Move node</li>
<li><b>Middle Click + Drag:</b> Pan canvas</li>
<li><b>Mouse Wheel:</b> Zoom in/out</li>
<li><b>Left Click + Drag (input/output):</b> Create edge</li>
</ul>

<p><b>Keyboard Shortcuts:</b></p>
<ul>
<li><b>Ctrl+N:</b> New graph</li>
<li><b>Ctrl+O:</b> Load graph</li>
<li><b>Ctrl+S:</b> Save graph</li>
<li><b>Ctrl+Q:</b> Exit</li>
<li><b>Ctrl+ +:</b> Zoom in</li>
<li><b>Ctrl+ -:</b> Zoom out</li>
<li><b>Ctrl+0:</b> Reset zoom</li>
<li><b>Delete/Backspace:</b> Delete selected edge</li>
</ul>

<p><b>Edge Creation:</b></p>
<ul>
<li>Drag from <span style="color:blue;">blue output circle</span> to <span style="color:red;">red input circle</span></li>
<li>Click on edge to select it, then press Delete to remove</li>
</ul>
        """
        
        QMessageBox.information(self, "Controls", controls_text)

    def import_json(self):
        """Import complete node graph from JSON file"""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Node Graph", "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as json_file:
                    data = json.load(json_file)
                    
                    # Validate data format
                    if 'nodes' not in data:
                        QMessageBox.warning(self, "Import Error", "Invalid file format: No 'nodes' data found.")
                        return
                    
                    # Clear existing nodes and edges
                    self.scene.clear()
                    self.node_items.clear()
                    
                    # Create nodes with complete data restoration
                    nodes = {}
                    for node_data in data['nodes']:
                        # Create appropriate node type based on saved type
                        node_type = node_data.get('type', 'normal')
                        if node_type == 'start':
                            node = StartNode(node_data['x'], node_data['y'], name=node_data['name'])
                        else:
                            node = NodeScene(node_data['x'], node_data['y'], name=node_data['name'])
                        
                        # Restore form data if available
                        if 'form_data' in node_data:
                            node.node_data = node_data['form_data']
                        
                        # Restore connection tracking
                        node.input_connected_node = node_data.get('input_connected_node', None)
                        node.output_connected_node = node_data.get('output_connected_node', None)
                        
                        # Add to scene and tracking
                        nodes[node_data['id']] = node
                        self.scene.addItem(node)
                        self.node_items.append(node)
                    
                    # Create edges with proper connections
                    if 'edges' in data:
                        for edge_data in data['edges']:
                            start_node = nodes.get(edge_data['start_node'])
                            end_node = nodes.get(edge_data['end_node'])
                            
                            if start_node and end_node:
                                # Create edge from output of start node to input of end node
                                start_pos = start_node.output_circle.mapToScene(start_node.output_circle.rect().center())
                                end_pos = end_node.input_circle.mapToScene(end_node.input_circle.rect().center()) if end_node.input_circle else end_node.output_circle.mapToScene(end_node.output_circle.rect().center())
                                
                                edge = EdgeGraphicsItem(start_pos, end_pos, QColor(0, 150, 255))
                                edge.start_circle = start_node.output_circle
                                edge.end_circle = end_node.input_circle if end_node.input_circle else end_node.output_circle
                                edge.updateFromNodes()
                                
                                # Add to scene
                                self.scene.addItem(edge)
                                
                                # Connect to circles
                                if not hasattr(start_node.output_circle, 'connected_edges'):
                                    start_node.output_circle.connected_edges = []
                                target_circle = end_node.input_circle if end_node.input_circle else end_node.output_circle
                                if not hasattr(target_circle, 'connected_edges'):
                                    target_circle.connected_edges = []
                                
                                start_node.output_circle.connected_edges.append(edge)
                                target_circle.connected_edges.append(edge)
                                
                                # Update connection tracking
                                start_node.output_connected_node = end_node.name
                                end_node.input_connected_node = start_node.name
                    
                    # Update scene rect to fit all nodes
                    if nodes:
                        all_rects = [node.sceneBoundingRect() for node in nodes.values()]
                        if all_rects:
                            union_rect = all_rects[0]
                            for rect in all_rects[1:]:
                                union_rect = union_rect.united(rect)
                            
                            # Add padding
                            padding = 100
                            union_rect = union_rect.adjusted(-padding, -padding, padding, padding)
                            self.scene.setSceneRect(union_rect)
                    
                    QMessageBox.information(self, "Import Successful", 
                                          f"Node graph loaded successfully!\n\nNodes: {len(nodes)}\nEdges: {len(data.get('edges', []))}")
                    
            except json.JSONDecodeError as e:
                QMessageBox.critical(self, "Import Error", f"Invalid JSON file format:\n{str(e)}")
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to load node graph:\n{str(e)}")

    def export_json(self):
        """Export complete node graph data to JSON file"""
        # Update all connection data first
        self.update_all_connections()
        
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Node Graph", "untitled_graph.json", "JSON Files (*.json);;All Files (*)", options=options)
        if file_name:
            try:
                # Ensure .json extension
                if not file_name.lower().endswith('.json'):
                    file_name += '.json'
                
                data = {
                    'version': '1.0',
                    'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'nodes': [],
                    'edges': []
                }
                
                # Collect complete node data including form data and connections
                for node in self.node_items:
                    node_data = {
                        'id': node.name,
                        'name': node.name,
                        'x': node.x(),
                        'y': node.y(),
                        'type': 'start' if isinstance(node, StartNode) else 'normal',
                        'input_connected_node': node.input_connected_node,
                        'output_connected_node': node.output_connected_node,
                        'form_data': node.node_data  # Complete form data including items, dialogs, actions
                    }
                    data['nodes'].append(node_data)
                
                # Collect edge data with unique IDs
                edge_id = 1
                for item in self.scene.items():
                    if isinstance(item, EdgeGraphicsItem):
                        if hasattr(item, 'start_circle') and hasattr(item, 'end_circle'):
                            start_node = item.start_circle.parentItem()
                            end_node = item.end_circle.parentItem()
                            if start_node and end_node:
                                edge_data = {
                                    'id': f"edge_{edge_id}",
                                    'start_node': start_node.name,
                                    'end_node': end_node.name,
                                    'start_point': 'output',  # Always from output to input
                                    'end_point': 'input'
                                }
                                data['edges'].append(edge_data)
                                edge_id += 1
                
                # Write to JSON file with pretty formatting
                with open(file_name, 'w', encoding='utf-8') as json_file:
                    json.dump(data, json_file, ensure_ascii=False, indent=2)
                
                # Show success message with file path
                file_size = os.path.getsize(file_name)
                self.status_bar.showMessage(f"Graph saved to {os.path.basename(file_name)} ({file_size} bytes)", 5000)
                
                QMessageBox.information(self, "Export Successful", 
                                      f"Node graph saved successfully!\n\nFile: {os.path.basename(file_name)}\nNodes: {len(data['nodes'])}\nEdges: {len(data['edges'])}")
                
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to save node graph:\n{str(e)}")

    def show_about(self):
        """Show about dialog"""
        about_text = """
<h3>Visual Novel Node Editor</h3>
<p><b>Version:</b> 2.0</p>
<p><b>Built with:</b> PySide6 (Qt for Python)</p>

<p>A modern node-based editor for visual novel scripting with support for:</p>
<ul>
<li>Interactive node graph editing</li>
<li>Dialog and action sequence management</li>
<li>Drag-and-drop row reordering</li>
<li>Complete graph save/load system</li>
<li>Canvas panning and zooming</li>
<li>Connection tracking between nodes</li>
</ul>

<p><b>Features:</b></p>
<ul>
<li>Thai font support (Sarabun)</li>
<li>Dark theme UI</li>
<li>JSON export/import</li>
<li>Keyboard shortcuts</li>
<li>Bezier curve connections</li>
</ul>

<p>Right-click to create nodes, double-click to edit, drag to connect!</p>
        """
        
        
        QMessageBox.about(self, "About Visual Novel Node Editor", about_text)
    
    def get_connected_nodes_sequence(self):
        """Get sequence of connected nodes starting from StartNode"""
        sequence = []
        
        # Find StartNode
        start_node = None
        for node in self.node_items:
            if isinstance(node, StartNode):
                start_node = node
                break
        
        print(f"Found StartNode: {start_node.name if start_node else 'None'}")
        
        if not start_node:
            return sequence
        
        # Debug: Print all nodes and their connections
        print("=== ALL NODES DEBUG ===")
        for i, node in enumerate(self.node_items):
            print(f"Node {i}: {node.name} (type: {type(node).__name__})")
            print(f"  Input connected to: {getattr(node, 'input_connected_node', 'N/A')}")
            print(f"  Output connected to: {getattr(node, 'output_connected_node', 'N/A')}")
            print(f"  Has node_data: {bool(getattr(node, 'node_data', None))}")
            if hasattr(node, 'node_data') and node.node_data:
                items_count = len(node.node_data.get('items', []))
                print(f"  Node data items: {items_count}")
        print("=== END DEBUG ===")
        
        # Traverse from start node following connections
        visited = set()
        current = start_node
        
        while current and current not in visited:
            visited.add(current)
            sequence.append(current)
            print(f"Added to sequence: {current.name} (output_connected_node: {current.output_connected_node})")
            
            # Find next connected node through output
            next_node = None
            if current.output_connected_node:
                for node in self.node_items:
                    if node.name == current.output_connected_node:
                        next_node = node
                        print(f"Found next node: {next_node.name}")
                        break
                if not next_node:
                    print(f"Could not find node with name: {current.output_connected_node}")
            else:
                print(f"Node {current.name} has no output connection")
            
            current = next_node
        
        print(f"Final sequence length: {len(sequence)}")
        return sequence
    
    def update_all_connections(self):
        """Update connection tracking for all nodes to ensure current data"""
        updated_count = 0
        print("=== UPDATING CONNECTIONS ===")
        for node in self.node_items:
            if isinstance(node, (NodeScene, StartNode)):
                print(f"Updating connections for: {node.name}")
                old_input = getattr(node, 'input_connected_node', None)
                old_output = getattr(node, 'output_connected_node', None)
                
                node.updateConnectionTracking()
                updated_count += 1
                
                new_input = getattr(node, 'input_connected_node', None)
                new_output = getattr(node, 'output_connected_node', None)
                
                print(f"  Input: {old_input} -> {new_input}")
                print(f"  Output: {old_output} -> {new_output}")
        
        print("=== CONNECTION UPDATE COMPLETE ===")
        # Show status message
        self.status_bar.showMessage(f"Updated connection data for {updated_count} nodes", 2000)
        print(f"Updated connection tracking for {updated_count} nodes before export")
    
    def export_connected_nodes_text(self):
        """Export connected nodes data as screenplay format"""
        # Update all connection data first
        self.update_all_connections()
        
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Export as Screenplay", "screenplay.txt", 
            "Text Files (*.txt);;All Files (*)", options=options
        )
        
        if file_name:
            try:
                if not file_name.lower().endswith('.txt'):
                    file_name += '.txt'
                
                sequence = self.get_connected_nodes_sequence()
                
                with open(file_name, 'w', encoding='utf-8') as f:
                    # Screenplay title page (optional header)
                    f.write("VISUAL NOVEL SCREENPLAY\n\n")
                    f.write(f"Generated: {time.strftime('%B %d, %Y')}\n")
                    f.write("\n" + "="*60 + "\n\n")
                    
                    # Track scene continuity
                    last_scene_location = ""
                    scene_number = 1
                    
                    for i, node in enumerate(sequence, 1):
                        if node.node_data:
                            # Scene header information
                            scene_type = node.node_data.get('scene_type', 'INT.')
                            name = node.node_data.get('name', '')
                            time_desc = node.node_data.get('time_description', '')
                            in_scene = node.node_data.get('in_scene', '')
                            out_scene = node.node_data.get('out_scene', '')
                            background = node.node_data.get('background', '')
                            
                            # Format scene heading (only if location/time changes)
                            current_scene_location = f"{scene_type} {name}".strip()
                            if current_scene_location != last_scene_location and current_scene_location != "INT." and current_scene_location != "EXT.":
                                f.write(f"{scene_number}. {scene_type} {name}")
                                if time_desc:
                                    f.write(f" - {time_desc}")
                                f.write("\n\n")
                                last_scene_location = current_scene_location
                                scene_number += 1
                            
                            # Scene transition IN
                            if in_scene and in_scene != "None":
                                if in_scene == "FADE IN":
                                    f.write("FADE IN:\n\n")
                                elif in_scene != "Other":
                                    f.write(f"{in_scene}:\n\n")
                            
                            # Background/Setting description (as action)
                            if background:
                                f.write(f"{background}\n\n")
                            
                            # Write screenplay content in order
                            if 'items' in node.node_data and node.node_data['items']:
                                for item in node.node_data['items']:
                                    if item['type'] == 'dialog':
                                        character = item.get('character', '').upper()
                                        parentheticals = item.get('parentheticals', '')
                                        text = item.get('text', '')
                                        
                                        if character:
                                            # Character name (centered, uppercase)
                                            f.write(f"                    {character}\n")
                                            
                                            # Parentheticals (if any)
                                            if parentheticals:
                                                f.write(f"                 ({parentheticals})\n")
                                            
                                            # Dialog text (indented)
                                            if text:
                                                # Wrap long lines for readability
                                                words = text.split()
                                                lines = []
                                                current_line = ""
                                                for word in words:
                                                    if len(current_line + word) < 50:  # Max character width
                                                        current_line += word + " "
                                                    else:
                                                        lines.append(current_line.strip())
                                                        current_line = word + " "
                                                if current_line:
                                                    lines.append(current_line.strip())
                                                
                                                for line in lines:
                                                    f.write(f"              {line}\n")
                                            
                                            f.write("\n")
                                    
                                    elif item['type'] == 'action':
                                        action_text = item.get('text', '')
                                        if action_text:
                                            # Action lines (full width, uppercase for emphasis)
                                            # Wrap action text
                                            words = action_text.split()
                                            lines = []
                                            current_line = ""
                                            for word in words:
                                                if len(current_line + word) < 65:  # Max action width
                                                    current_line += word + " "
                                                else:
                                                    lines.append(current_line.strip())
                                                    current_line = word + " "
                                            if current_line:
                                                lines.append(current_line.strip())
                                            
                                            for line in lines:
                                                f.write(f"{line}\n")
                                            
                                            f.write("\n")
                            
                            # Scene transition OUT
                            if out_scene and out_scene != "None":
                                if out_scene in ["CUT TO", "DISSOLVE TO", "FADE OUT"]:
                                    f.write(f"                              {out_scene}:\n\n")
                                elif out_scene == "Other":
                                    # Custom transition would be handled in the form
                                    pass
                        
                        # Add extra spacing between major scenes
                        if i < len(sequence):
                            f.write("\n")
                    
                    # End screenplay
                    f.write("\n                              FADE OUT.\n\n")
                    f.write("                                END\n")
                
                QMessageBox.information(self, "Export Successful", 
                    f"Screenplay exported successfully!\n\nFile: {os.path.basename(file_name)}\nScenes: {len(sequence)}")
                    
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export screenplay:\n{str(e)}")
    
    def export_connected_nodes_json(self):
        """Export connected nodes data as structured JSON"""
        # Update all connection data first
        self.update_all_connections()
        
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Export Node Data as JSON", "node_sequence.json", 
            "JSON Files (*.json);;All Files (*)", options=options
        )
        
        if file_name:
            try:
                if not file_name.lower().endswith('.json'):
                    file_name += '.json'
                
                sequence = self.get_connected_nodes_sequence()
                
                export_data = {
                    'metadata': {
                        'title': 'Visual Novel Node Sequence',
                        'generated': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'total_nodes': len(sequence),
                        'version': '1.0'
                    },
                    'sequence': []
                }
                
                for i, node in enumerate(sequence, 1):
                    node_data = {
                        'sequence_number': i,
                        'name': node.name,
                        'type': 'Start Node' if isinstance(node, StartNode) else 'Regular Node',
                        'scene_type': node.node_data.get('scene_type', '') if node.node_data else '',
                        'scene_name': node.node_data.get('name', '') if node.node_data else '',
                        'time_description': node.node_data.get('time_description', '') if node.node_data else '',
                        'in_scene': node.node_data.get('in_scene', '') if node.node_data else '',
                        'out_scene': node.node_data.get('out_scene', '') if node.node_data else '',
                        'background': node.node_data.get('background', '') if node.node_data else '',
                        'content':  node.node_data.get('items', []) if node.node_data else [],
                        'connections': {
                            'input_from': node.input_connected_node,
                            'output_to': node.output_connected_node
                        }
                        
                    }
                    export_data['sequence'].append(node_data)
                
                with open(file_name, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                
                file_size = os.path.getsize(file_name)
                QMessageBox.information(self, "Export Successful", 
                    f"Node sequence exported successfully!\n\nFile: {os.path.basename(file_name)}\nNodes: {len(sequence)}\nSize: {file_size} bytes")
                    
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export JSON:\n{str(e)}")
    
    def export_connected_nodes_csv(self):
        """Export connected nodes data as CSV for spreadsheet analysis"""
        # Update all connection data first
        self.update_all_connections()
        
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Export Node Data as CSV", "node_sequence.csv", 
            "CSV Files (*.csv);;All Files (*)", options=options
        )
        
        if file_name:
            try:
                if not file_name.lower().endswith('.csv'):
                    file_name += '.csv'
                
                sequence = self.get_connected_nodes_sequence()
                
                with open(file_name, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    
                    # Header
                    writer.writerow([
                        'Sequence', 'Node Name', 'Type', 'Scene Type', 'Scene Name', 'Time Description', 
                        'In Scene', 'Out Scene', 'Background', 'Item Order', 'Item Type', 'Character', 'Parentheticals', 'Text', 'Input From', 'Output To'
                    ])
                    
                    for i, node in enumerate(sequence, 1):
                        base_row = [
                            i, node.name, 
                            'Start Node' if isinstance(node, StartNode) else 'Regular Node',
                            node.node_data.get('scene_type', '') if node.node_data else '',
                            node.node_data.get('name', '') if node.node_data else '',
                            node.node_data.get('time_description', '') if node.node_data else '',
                            node.node_data.get('in_scene', '') if node.node_data else '',
                            node.node_data.get('out_scene', '') if node.node_data else '',
                            node.node_data.get('background', '') if node.node_data else '',
                        ]
                        
                        if node.node_data and 'items' in node.node_data and node.node_data['items']:
                            # Write each item as a separate row
                            for item in node.node_data['items']:
                                row = base_row + [
                                    item.get('order', ''),
                                    item.get('type', ''),
                                    item.get('character', '') if item.get('type') == 'dialog' else '',
                                    item.get('parentheticals', '') if item.get('type') == 'dialog' else '',
                                    item.get('text', ''),
                                    node.input_connected_node or '',
                                    node.output_connected_node or ''
                                ]
                                writer.writerow(row)
                        else:
                            # Empty content row
                            row = base_row + ['', '', '', '', '', 
                                            node.input_connected_node or '',
                                            node.output_connected_node or '']
                            writer.writerow(row)
                
                QMessageBox.information(self, "Export Successful", 
                    f"Node sequence exported successfully!\n\nFile: {os.path.basename(file_name)}\nNodes: {len(sequence)}")
                    
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export CSV:\n{str(e)}")
    
    def export_connected_nodes_pdf(self):
        """Export connected nodes data as PDF screenplay in A4 format"""
        if not PDF_AVAILABLE:
            QMessageBox.warning(self, "PDF Export Not Available", 
                              "PDF export requires the 'reportlab' library.\n\nInstall it with: pip install reportlab")
            return
            
        # Update all connection data first
        self.update_all_connections()
        
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Export as PDF Screenplay", "screenplay.pdf", 
            "PDF Files (*.pdf);;All Files (*)", options=options
        )
        
        if file_name:
            try:
                if not file_name.lower().endswith('.pdf'):
                    file_name += '.pdf'
                
                sequence = self.get_connected_nodes_sequence()
                
                # Create PDF document with A4 page size
                doc = SimpleDocTemplate(file_name, pagesize=A4,
                                      rightMargin=1*inch, leftMargin=1.5*inch,
                                      topMargin=1*inch, bottomMargin=1*inch)
                
                # Create story (content) list
                story = []
                
                # Register Thai fonts (Sarabun)
                try:
                    # Get the path to Sarabun fonts
                    sarabun_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Sarabun')
                    
                    # Register Sarabun fonts
                    pdfmetrics.registerFont(TTFont('Sarabun', os.path.join(sarabun_path, 'Sarabun-Regular.ttf')))
                    pdfmetrics.registerFont(TTFont('Sarabun-Bold', os.path.join(sarabun_path, 'Sarabun-Bold.ttf')))
                    pdfmetrics.registerFont(TTFont('Sarabun-Italic', os.path.join(sarabun_path, 'Sarabun-Italic.ttf')))
                    pdfmetrics.registerFont(TTFont('Sarabun-BoldItalic', os.path.join(sarabun_path, 'Sarabun-BoldItalic.ttf')))
                    
                    # Create font family
                    registerFontFamily('Sarabun', normal='Sarabun', bold='Sarabun-Bold', 
                                     italic='Sarabun-Italic', boldItalic='Sarabun-BoldItalic')
                    
                    thai_font = 'Sarabun'
                    thai_font_bold = 'Sarabun-Bold'
                    print("Thai fonts (Sarabun) registered successfully")
                except Exception as e:
                    print(f"Could not register Thai fonts: {e}")
                    print("Using default fonts instead")
                    thai_font = 'Helvetica'
                    thai_font_bold = 'Helvetica-Bold'
                
                # Define custom styles for screenplay formatting with Thai font support
                styles = getSampleStyleSheet()
                
                # Title style
                title_style = ParagraphStyle('CustomTitle',
                                           parent=styles['Heading1'],
                                           fontSize=16,
                                           fontName=thai_font_bold,
                                           spaceAfter=30,
                                           alignment=TA_CENTER)
                
                # Scene heading style
                scene_style = ParagraphStyle('SceneHeading',
                                           parent=styles['Normal'],
                                           fontSize=12,
                                           fontName=thai_font_bold,
                                           spaceBefore=6,
                                           alignment=TA_LEFT)
                
                # Character name style (centered)
                character_style = ParagraphStyle('Character',
                                               parent=styles['Normal'],
                                               fontSize=12,
                                               fontName=thai_font,
                                               spaceBefore=6,
                                               alignment=TA_CENTER,
                                               leftIndent=2.2*inch,
                                               rightIndent=1*inch)
                
                # Parenthetical style
                parenthetical_style = ParagraphStyle('Parenthetical',
                                                   parent=styles['Normal'],
                                                   fontSize=11,
                                                   fontName=thai_font,
                                                   alignment=TA_LEFT,
                                                   leftIndent=2.5*inch,
                                                   rightIndent=1.5*inch)
                
                # Dialog style
                dialog_style = ParagraphStyle('Dialog',
                                            parent=styles['Normal'],
                                            fontSize=12,
                                            fontName=thai_font,
                                            alignment=TA_LEFT,
                                            leftIndent=1.5*inch,
                                            rightIndent=1*inch)
                
                # Action style
                action_style = ParagraphStyle('Action',
                                            parent=styles['Normal'],
                                            fontSize=12,
                                            fontName=thai_font,
                                            spaceBefore=6,
                                            alignment=TA_LEFT)
                
                # Transition style (right aligned)
                transition_style = ParagraphStyle('Transition',
                                                parent=styles['Normal'],
                                                fontSize=12,
                                                fontName=thai_font,
                                                spaceBefore=6,
                                                alignment=TA_RIGHT)
                
                # Add title
                story.append(Paragraph("VISUAL NOVEL SCREENPLAY", title_style))
                story.append(Paragraph(f"Generated: {time.strftime('%B %d, %Y')}", styles['Normal']))
                story.append(Spacer(1, 20))
                
                # Track scene continuity
                last_scene_location = ""
                scene_number = 1
                
                for i, node in enumerate(sequence, 1):
                    if node.node_data:
                        # Scene header information
                        sequence_number = node.node_data.get('sequence_number', i)
                        scene_type = node.node_data.get('scene_type', 'INT.')
                        name = node.node_data.get('name', '')
                        time_desc = node.node_data.get('time_description', '')
                        in_scene = node.node_data.get('in_scene', '')
                        out_scene = node.node_data.get('out_scene', '')
                        background = node.node_data.get('background', '')
                        
                        # Scene transition IN
                        if in_scene and in_scene != "None":
                            if in_scene == "FADE IN":
                                story.append(Paragraph("FADE IN:", action_style))
                            elif in_scene != "Other":
                                story.append(Paragraph(f"{in_scene}:", action_style))

                        # Format scene heading (only if location/time changes)
                        current_scene_location = f"{scene_type} {name}".strip()
                        if current_scene_location != last_scene_location and current_scene_location not in ["INT.", "EXT."]:
                            scene_heading = f"({sequence_number}) {scene_type} {name}"
                            if time_desc:
                                scene_heading += f" - {time_desc}"
                            story.append(Paragraph(scene_heading.upper(), scene_style))
                            last_scene_location = current_scene_location
                            scene_number += 1
                        
                        
                        # Background/Setting description
                        if background:
                            story.append(Paragraph(background, action_style))
                        
                        # Write screenplay content in order
                        if 'items' in node.node_data and node.node_data['items']:
                            for item in node.node_data['items']:
                                if item['type'] == 'dialog':
                                    character = item.get('character', '').upper()
                                    parentheticals = item.get('parentheticals', '')
                                    text = item.get('text', '')
                                    
                                    if character:
                                        # Character name
                                        story.append(Paragraph(character, character_style))
                                        
                                        # Parentheticals (if any)
                                        if parentheticals:
                                            story.append(Paragraph(f"({parentheticals})", parenthetical_style))
                                        
                                        # Dialog text
                                        if text:
                                            story.append(Paragraph(text, dialog_style))
                                
                                elif item['type'] == 'action':
                                    action_text = item.get('text', '')
                                    if action_text:
                                        story.append(Paragraph(action_text, action_style))
                        
                        # Scene transition OUT
                        if out_scene and out_scene != "None":
                            if out_scene in ["CUT TO", "DISSOLVE TO", "FADE OUT"]:
                                story.append(Paragraph(f"{out_scene}:", transition_style))
                    
                    # Add spacing between nodes if not the last one
                    if i < len(sequence):
                        story.append(Spacer(1, 12))
                
                # End screenplay
            
                
                # Create style for END with Thai font
                end_style = ParagraphStyle('End',
                                         parent=styles['Normal'],
                                         fontSize=12,
                                         fontName=thai_font,
                                         alignment=TA_CENTER)
                story.append(Paragraph("END", end_style))
                
                # Build PDF
                doc.build(story)
                
                file_size = os.path.getsize(file_name)
                QMessageBox.information(self, "Export Successful", 
                    f"PDF screenplay exported successfully!\n\nFile: {os.path.basename(file_name)}\nScenes: {len(sequence)}\nSize: {file_size/1024:.1f} KB")
                    
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export PDF:\n{str(e)}")
    
    def eventFilter(self, obj, event):
        if obj == self.view.viewport():
            # ตรวจสอบว่าคลิกที่โหนดหรือไม่
            scene_pos = self.view.mapToScene(event.position().toPoint()) if hasattr(event, 'position') else None
            item_at_pos = self.scene.itemAt(scene_pos, self.view.transform()) if scene_pos is not None else None
            if event.type() == QEvent.MouseButtonPress:
                if hasattr(event, 'button') and event.button() == Qt.MiddleButton:
                    # เริ่ม canvas panning ด้วยเมาส์กลาง
                    if item_at_pos is None:
                        self._dragging = True
                        self._drag_start = event.pos()
                        return True
                elif hasattr(event, 'button') and event.button() == Qt.RightButton:
                    if item_at_pos is None:
                        pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
                        scene_pos = self.view.mapToScene(pos)
                        node = NodeScene(scene_pos.x(), scene_pos.y())
                        self.scene.addItem(node)
                        self.node_items.append(node)
                        
                        # Show status message
                        self.status_bar.showMessage(f"Created new node '{node.name}'", 3000)
                        
                        # --- Expand scene rect if needed ---
                        node_rect = node.sceneBoundingRect()
                        scene_rect = self.scene.sceneRect()
                        # เพิ่ม offset เพื่อขยายขอบเขต scene ให้มีพื้นที่รอบ node
                        offset = 40
                        node_rect = node_rect.adjusted(-offset, -offset, offset, offset)
                        new_rect = scene_rect.united(node_rect)
                        self.scene.setSceneRect(new_rect)
                        return True
            elif event.type() == QEvent.MouseMove:
                if self._dragging and self._drag_start is not None and hasattr(event, 'pos'):
                    # Canvas panning ด้วยเมาส์กลาง
                    delta = event.pos() - self._drag_start
                    self.view.horizontalScrollBar().setValue(self.view.horizontalScrollBar().value() - delta.x())
                    self.view.verticalScrollBar().setValue(self.view.verticalScrollBar().value() - delta.y())
                    self._drag_start = event.pos()
                    # --- Expand scene rect if panned out of bounds ---
                    view_rect = self.view.mapToScene(self.view.viewport().rect()).boundingRect()
                    scene_rect = self.scene.sceneRect()
                    new_rect = scene_rect.united(view_rect)
                    self.scene.setSceneRect(new_rect)
                    return True
            elif event.type() == QEvent.MouseButtonRelease:
                if hasattr(event, 'button') and event.button() == Qt.MiddleButton:
                    # สิ้นสุด canvas panning
                    self._dragging = False
                    self._drag_start = None
                    return True
        return super().eventFilter(obj, event)

    def update_status(self):
        """Update status bar with current graph information"""
        nodes_count = len(self.node_items)
        edges_count = len([item for item in self.scene.items() if isinstance(item, EdgeGraphicsItem)])
        zoom_level = int(self.view._zoom * 100) if hasattr(self.view, '_zoom') else 100
        
        self.status_bar.showMessage(f"Nodes: {nodes_count} | Edges: {edges_count} | Zoom: {zoom_level}%")
    
    def create_default_start_node(self):
        """Create a default start node at the center-left of the canvas"""
        # Calculate position (left side of the visible area)
        scene_rect = self.scene.sceneRect()
        start_x = scene_rect.x() + 100  # 100 pixels from left edge
        start_y = scene_rect.center().y()  # Center vertically
        
        # Create start node
        start_node = StartNode(start_x, start_y, name="Start")
        self.scene.addItem(start_node)
        self.node_items.append(start_node)
        
        # Show status message
        self.status_bar.showMessage("Default Start node created - Right-click to add more nodes", 3000)
        
        print(f"Created default Start node at position ({start_x}, {start_y})")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
