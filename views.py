"""
Custom Views for Visual Novel Node Editor
Contains NodeGraphicsView with zoom, keyboard handling, visual enhancements, and context menu
"""

from PySide6.QtWidgets import QGraphicsView, QMenu
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor


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
                # Import here to avoid circular import
                from graphics_items import EdgeGraphicsItem
                if isinstance(item, EdgeGraphicsItem):
                    # Remove from connections before deleting
                    item.removeFromConnections()
                    self.scene().removeItem(item)
            event.accept()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            # Check if right-click is on empty area (not on any item)
            scene_pos = self.mapToScene(event.pos())
            item_at_pos = self.scene().itemAt(scene_pos, self.transform())
            
            if item_at_pos is None:
                # Right-click on empty area - show context menu
                self.show_context_menu(event.globalPos(), scene_pos)
                event.accept()
                return
            else:
                # Check if right-click is on a Branch node - let it handle its own context menu
                from graphics_items import BranchNode
                if isinstance(item_at_pos, BranchNode):
                    # Let the BranchNode handle the right-click
                    super().mousePressEvent(event)
                    return
        
        # Let the base class handle other events
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # Handle right-click release for context menu (backup approach)
        if event.button() == Qt.RightButton:
            scene_pos = self.mapToScene(event.pos())
            item_at_pos = self.scene().itemAt(scene_pos, self.transform())
            
            if item_at_pos is None:
                # Right-click on empty area - show context menu
                self.show_context_menu(event.globalPos(), scene_pos)
                event.accept()
                return
            else:
                # Check if right-click is on a Branch node - let it handle its own context menu
                from graphics_items import BranchNode
                if isinstance(item_at_pos, BranchNode):
                    # Let the BranchNode handle the right-click
                    super().mouseReleaseEvent(event)
                    return
        
        super().mouseReleaseEvent(event)

    def show_context_menu(self, global_pos, scene_pos):
        """Show context menu for creating nodes"""
        menu = QMenu(self)
        
        # Add node creation actions
        create_start_action = menu.addAction("🚀 Create Start Node")
        create_scene_action = menu.addAction("🎬 Create Scene Node")
        menu.addSeparator()
        create_branch_action = menu.addAction("🌿 Create Branch Node")
        
        # Execute menu and handle selection
        action = menu.exec(global_pos)
        
        if action == create_start_action:
            self.create_start_node(scene_pos)
        elif action == create_scene_action:
            self.create_scene_node(scene_pos)
        elif action == create_branch_action:
            self.create_branch_node(scene_pos)
        elif action == create_branch_action:
            self.create_branch_node(scene_pos)

    def create_start_node(self, scene_pos):
        """Create a new start node at the specified position"""
        # Get main window for access to node_items list
        main_window = self.window()
        if main_window and hasattr(main_window, 'node_items'):
            # Import here to avoid circular import
            from graphics_items import StartNode
            
            # Create start node at clicked position
            start_node = StartNode(scene_pos.x() - 60, scene_pos.y() - 30)
            self.scene().addItem(start_node)
            main_window.node_items.append(start_node)
            
            # Update scene rect to include new node
            self.update_scene_rect_for_node(start_node)
            
            # Show status message
            if hasattr(main_window, 'status_bar'):
                main_window.status_bar.showMessage(f"Created start node '{start_node.name}'", 3000)
            
            print(f"Created start node '{start_node.name}' at position ({scene_pos.x()}, {scene_pos.y()})")

    def create_scene_node(self, scene_pos):
        """Create a new scene node at the specified position"""
        # Get main window for access to node_items list
        main_window = self.window()
        if main_window and hasattr(main_window, 'node_items'):
            # Import here to avoid circular import
            from graphics_items import NodeScene
            
            # Create scene node at clicked position
            scene_node = NodeScene(scene_pos.x() - 60, scene_pos.y() - 30)
            self.scene().addItem(scene_node)
            main_window.node_items.append(scene_node)
            
            # Update scene rect to include new node
            self.update_scene_rect_for_node(scene_node)
            
            # Show status message
            if hasattr(main_window, 'status_bar'):
                main_window.status_bar.showMessage(f"Created scene node '{scene_node.name}'", 3000)
            
            print(f"Created scene node '{scene_node.name}' at position ({scene_pos.x()}, {scene_pos.y()})")

    def create_branch_node(self, scene_pos):
        """Create a new branch node at the specified position"""
        # Get main window for access to node_items list
        main_window = self.window()
        if main_window and hasattr(main_window, 'node_items'):
            # Import here to avoid circular import
            from graphics_items import BranchNode
            
            # Create branch node at clicked position
            branch_node = BranchNode(scene_pos.x() - 60, scene_pos.y() - 30)
            self.scene().addItem(branch_node)
            main_window.node_items.append(branch_node)
            
            # Update scene rect to include new node
            self.update_scene_rect_for_node(branch_node)
            
            # Show status message
            if hasattr(main_window, 'status_bar'):
                main_window.status_bar.showMessage(f"Created branch node '{branch_node.name}'", 3000)
            
            print(f"Created branch node '{branch_node.name}' at position ({scene_pos.x()}, {scene_pos.y()})")

    def update_scene_rect_for_node(self, node):
        """Update scene rectangle to include the new node"""
        scene = self.scene()
        if scene:
            node_rect = node.sceneBoundingRect()
            scene_rect = scene.sceneRect()
            offset = 40
            node_rect = node_rect.adjusted(-offset, -offset, offset, offset)
            new_rect = scene_rect.united(node_rect)
            scene.setSceneRect(new_rect)

    def drawForeground(self, painter, rect):
        """Draw node names on top of everything"""
        # Set font for node names
        font = QFont("Arial", 10)
        painter.setFont(font)
        painter.setPen(QColor(0, 0, 0))
        
        # Draw names for all nodes
        for item in self.scene().items():
            # Import here to avoid circular import
            from graphics_items import NodeScene, StartNode, BranchNode
            if isinstance(item, (NodeScene, StartNode, BranchNode)):
                # Calculate text position (center of node)
                node_rect = item.sceneBoundingRect()
                text_rect = node_rect.adjusted(5, 5, -5, -5)
                
                # Use different color for different node types
                if isinstance(item, StartNode):
                    painter.setPen(QColor(0, 100, 0))    # Dark green for start node
                elif isinstance(item, BranchNode):
                    painter.setPen(QColor(100, 0, 100))  # Purple for branch node
                else:
                    painter.setPen(QColor(0, 0, 0))      # Black for regular nodes
                
                # Draw node name
                painter.drawText(text_rect, Qt.AlignCenter, item.name)
        
        super().drawForeground(painter, rect)
