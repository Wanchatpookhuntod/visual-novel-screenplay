"""
Custom Views for Visual Novel Node Editor
Contains NodeGraphicsView with zoom, keyboard handling, and visual enhancements
"""

from PySide6.QtWidgets import QGraphicsView
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

    def drawForeground(self, painter, rect):
        """Draw node names on top of everything"""
        # Set font for node names
        font = QFont("Arial", 10)
        painter.setFont(font)
        painter.setPen(QColor(0, 0, 0))
        
        # Draw names for all nodes
        for item in self.scene().items():
            # Import here to avoid circular import
            from graphics_items import NodeScene, StartNode
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
