"""
Main Window for Visual Novel Node Editor
Contains MainWindow class with all UI functionality and scene management
"""

import sys
import time
import json
import os
from PySide6.QtWidgets import (QMainWindow, QMenuBar, QMenu, QFileDialog, QMessageBox, 
                               QGraphicsScene, QStatusBar, QApplication)
from PySide6.QtCore import Qt, QTimer, QEvent
from PySide6.QtGui import QAction, QColor

# Import our custom modules
from views import NodeGraphicsView
from graphics_items import NodeScene, StartNode, EdgeGraphicsItem
from export_manager import ExportManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visual Novel Node Editor")
        self.showMaximized()
        self.setMinimumSize(800, 600)
        self.setWindowState(Qt.WindowMaximized)
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

        # Scene and view setup
        self.scene = QGraphicsScene()
        self.view = NodeGraphicsView(self.scene)
        self.setCentralWidget(self.view)
        self.scene.setSceneRect(0, 0, self.width(), self.height())
        
        # Enable focus for key events
        self.view.setFocusPolicy(Qt.StrongFocus)

        # Node tracking
        self.node_items = []

        # Mouse handling setup
        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)
        self._dragging = False
        self._drag_start = None

        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready - Right-click to show context menu, double-click to edit nodes")
        
        # Update status bar periodically
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(2000)  # Update every 2 seconds

        # Export manager
        self.export_manager = ExportManager(self)

        # Menu bar actions
        self.initMenuBar()
        
        # Create default start node
        self.create_default_start_node()

    def initMenuBar(self):
        """Initialize menu bar with all actions"""
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
        export_text_action.triggered.connect(self.export_manager.export_as_text)
        export_menu.addAction(export_text_action)
        
        # Export connected nodes as JSON
        export_json_action = QAction("Export Node Data as JSON...", self)
        export_json_action.triggered.connect(self.export_manager.export_as_json)
        export_menu.addAction(export_json_action)
        
        # Export as CSV
        export_csv_action = QAction("Export as CSV...", self)
        export_csv_action.triggered.connect(self.export_manager.export_as_csv)
        export_menu.addAction(export_csv_action)
        
        # Export as PDF
        export_pdf_action = QAction("Export as PDF Screenplay...", self)
        export_pdf_action.triggered.connect(self.export_manager.export_as_pdf)
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
<li><b>Right Click (empty area):</b> Show context menu to create nodes</li>
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

<p>Right-click to show context menu, double-click to edit, drag to connect!</p>
        """
        
        QMessageBox.about(self, "About Visual Novel Node Editor", about_text)

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
        self.export_manager.update_all_connections()
        
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

    def eventFilter(self, obj, event):
        """Handle mouse events for canvas interaction"""
        if obj == self.view.viewport():
            # Check if click is on a node
            scene_pos = self.view.mapToScene(event.position().toPoint()) if hasattr(event, 'position') else None
            item_at_pos = self.scene.itemAt(scene_pos, self.view.transform()) if scene_pos is not None else None
            
            if event.type() == QEvent.MouseButtonPress:
                if hasattr(event, 'button') and event.button() == Qt.MiddleButton:
                    # Start canvas panning with middle mouse
                    if item_at_pos is None:
                        self._dragging = True
                        self._drag_start = event.pos()
                        return True
                elif hasattr(event, 'button') and event.button() == Qt.RightButton:
                    if item_at_pos is None:
                        # Don't handle right-click here - let views.py handle it with context menu
                        return False  # Let the event propagate to views.py
                        
                        # OLD CODE: Create new node on right click (now handled by context menu)
                        # pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
                        # scene_pos = self.view.mapToScene(pos)
                        # node = NodeScene(scene_pos.x(), scene_pos.y())
                        # self.scene.addItem(node)
                        # self.node_items.append(node)
                        # 
                        # # Show status message
                        # self.status_bar.showMessage(f"Created new node '{node.name}'", 3000)
                        # 
                        # # Expand scene rect if needed
                        # node_rect = node.sceneBoundingRect()
                        # scene_rect = self.scene.sceneRect()
                        # offset = 40
                        # node_rect = node_rect.adjusted(-offset, -offset, offset, offset)
                        # new_rect = scene_rect.united(node_rect)
                        # self.scene.setSceneRect(new_rect)
                        # return True
            elif event.type() == QEvent.MouseMove:
                if self._dragging and self._drag_start is not None and hasattr(event, 'pos'):
                    # Canvas panning with middle mouse
                    delta = event.pos() - self._drag_start
                    self.view.horizontalScrollBar().setValue(self.view.horizontalScrollBar().value() - delta.x())
                    self.view.verticalScrollBar().setValue(self.view.verticalScrollBar().value() - delta.y())
                    self._drag_start = event.pos()
                    
                    # Expand scene rect if panned out of bounds
                    view_rect = self.view.mapToScene(self.view.viewport().rect()).boundingRect()
                    scene_rect = self.scene.sceneRect()
                    new_rect = scene_rect.united(view_rect)
                    self.scene.setSceneRect(new_rect)
                    return True
            elif event.type() == QEvent.MouseButtonRelease:
                if hasattr(event, 'button') and event.button() == Qt.MiddleButton:
                    # End canvas panning
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
        self.status_bar.showMessage("Default Start node created - Right-click to show context menu for more nodes", 3000)
        
        print(f"Created default Start node at position ({start_x}, {start_y})")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
