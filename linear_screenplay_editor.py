"""
Linear Screenplay Editor
โปรแกรมสร้าง screenplay แบบเพิ่ม form ไปเรื่อยๆ ไม่ต้องใช้ node
"""

import sys
import time
import json
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                               QWidget, QPushButton, QScrollArea, QFrame, QLabel,
                               QTextEdit, QComboBox, QLineEdit, QMenuBar, QMenu,
                               QFileDialog, QMessageBox, QSplitter, QGroupBox, QDialog)
from PySide6.QtCore import Qt, QMimeData, QPoint
from PySide6.QtGui import QAction, QFont, QDrag, QPainter

# Import export manager for PDF generation
from export_manager import ExportManager
# Import the existing form
from form import MyForm


class ScreenplayScene(QFrame):
    """Widget สำหรับ scene หนึ่งใน screenplay ที่ใช้ MyForm"""
    
    def __init__(self, scene_number=1, parent=None):
        super().__init__(parent)
        self.scene_number = scene_number
        self.parent_window = parent
        self.is_expanded = False  # เริ่มต้นในโหมด collapsed
        self.form_data = {}  # เก็บข้อมูลจาก form
        self.setAcceptDrops(True)
        self.drag_start_position = None
        self.drop_indicator = None  # เส้นแบ่งตำแหน่ง drop
        
        # ตั้งค่า context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        self.setup_ui()
        
    def setup_ui(self):
        """สร้าง UI สำหรับ scene"""
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(2)
        self.setStyleSheet("""
            ScreenplayScene {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 8px;
                margin: 0px;
                padding: 2px;
                max-height: 50px;
                min-height: 40px;
            }
            ScreenplayScene:hover {
                background-color: #e8e8e8;
                border-color: #999;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)
        
        # Header สำหรับ scene (แสดงตลอดเวลา)
        header_layout = QHBoxLayout()
        
        # Scene title และ summary ในแถวเดียวกัน
        self.scene_label = QLabel(f"SCENE {self.scene_number}")
        self.scene_label.setFont(QFont("Arial", 11, QFont.Bold))
        header_layout.addWidget(self.scene_label)
        
        # Summary label (แสดงข้อมูลสรุป)
        self.summary_label = QLabel("ดับเบิลคลิกเพื่อแก้ไข...")
        self.summary_label.setFont(QFont("Arial", 10))
        self.summary_label.setStyleSheet("color: #555; font-style: italic;")
        header_layout.addWidget(self.summary_label)
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Update summary
        self.update_summary()
        
    def open_form(self):
        """เปิด form สำหรับแก้ไข scene"""
        form = MyForm(self)
        
        # โหลดข้อมูลเดิม (ถ้ามี)
        if self.form_data:
            self.populate_form(form, self.form_data)
        
        # แสดง form
        if form.exec() == QDialog.Accepted:
            # บันทึกข้อมูลจาก form
            self.form_data = form.get_form_data()
            self.update_summary()
            
            # อัปเดต preview
            if self.parent_window:
                self.parent_window.update_preview()
    
    def populate_form(self, form, data):
        """โหลดข้อมูลลงใน form"""
        # Scene information
        if 'scene_type' in data:
            form.scene_type_combo.setCurrentText(data['scene_type'])
        if 'name' in data:
            form.name_input.setText(data['name'])
        if 'time_description' in data:
            form.time_input.setText(data['time_description'])
        if 'in_scene' in data:
            if data['in_scene'] in ["FADE IN"]:
                form.in_scene_combo.setCurrentText(data['in_scene'])
            else:
                form.in_scene_combo.setCurrentText("Other")
                form.in_scene_text.setText(data['in_scene'])
        if 'out_scene' in data:
            if data['out_scene'] in ["CUT TO", "DISSOLVE TO", "FADE OUT"]:
                form.out_scene_combo.setCurrentText(data['out_scene'])
            else:
                form.out_scene_combo.setCurrentText("Other")
                form.out_scene_text.setText(data['out_scene'])
        if 'background' in data:
            form.bg_input.setText(data['background'])
        
        # Clear existing rows
        form.clear_all_rows()
        
        # Add rows from data
        for item in data.get('items', []):
            form.add_row()
            row_data = form.rows[-1]  # Get the last added row
            
            if item['type'] == 'dialog':
                row_data['type_combo'].setCurrentText("Dialog")
                row_data['character'].setText(item.get('character', ''))
                row_data['parentheticals'].setText(item.get('parentheticals', ''))
                row_data['text'].setText(item.get('text', ''))
            elif item['type'] == 'action':
                row_data['type_combo'].setCurrentText("Action")
                row_data['text'].setText(item.get('text', ''))
    
    def mouseDoubleClickEvent(self, event):
        """จัดการ double click เพื่อเปิด form"""
        self.open_form()
        super().mouseDoubleClickEvent(event)
    
    def mousePressEvent(self, event):
        """เริ่มต้น drag operation"""
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.position().toPoint()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """จัดการ mouse move สำหรับ drag"""
        if not (event.buttons() & Qt.LeftButton):
            return
        if not self.drag_start_position:
            return
        
        # ตรวจสอบระยะทางที่เลื่อน
        if ((event.position().toPoint() - self.drag_start_position).manhattanLength() < 
            QApplication.startDragDistance()):
            return
        
        # เริ่ม drag operation
        drag = QDrag(self)
        mimeData = QMimeData()
        mimeData.setText(f"scene_{id(self)}")
        drag.setMimeData(mimeData)
        
        # สร้าง drag pixmap
        pixmap = self.grab()
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        painter.fillRect(pixmap.rect(), Qt.GlobalColor.black)
        painter.end()
        
        drag.setPixmap(pixmap)
        drag.setHotSpot(self.drag_start_position)
        
        # Execute drag
        drag.exec(Qt.MoveAction)
    
    def dragEnterEvent(self, event):
        """ยอมรับ drag event และแสดงเส้นแบ่ง"""
        if event.mimeData().hasText() and event.mimeData().text().startswith("scene_"):
            event.acceptProposedAction()
            self.show_drop_indicator()
    
    def dragMoveEvent(self, event):
        """อัปเดตตำแหน่งเส้นแบ่งตาม mouse position"""
        if event.mimeData().hasText() and event.mimeData().text().startswith("scene_"):
            event.acceptProposedAction()
            self.update_drop_indicator_position(event.position().toPoint())
    
    def dragLeaveEvent(self, event):
        """ซ่อนเส้นแบ่งเมื่อ drag ออกไป"""
        self.hide_drop_indicator()
        super().dragLeaveEvent(event)
    
    def show_drop_indicator(self):
        """แสดงเส้นแบ่งตำแหน่ง drop"""
        if not self.drop_indicator:
            self.drop_indicator = QFrame(self.parent())
            self.drop_indicator.setFrameStyle(QFrame.HLine)
            self.drop_indicator.setStyleSheet("""
                QFrame {
                    background-color: #3498db;
                    border: 2px solid #2980b9;
                    height: 4px;
                    border-radius: 2px;
                    margin: 0px;
                }
            """)
            self.drop_indicator.setFixedHeight(4)
        
        # Position the indicator above this widget
        pos = self.pos()
        parent_width = self.parent().width() if self.parent() else self.width()
        self.drop_indicator.setGeometry(10, pos.y() - 3, parent_width - 20, 4)
        self.drop_indicator.show()
        self.drop_indicator.raise_()
    
    def update_drop_indicator_position(self, mouse_pos):
        """อัปเดตตำแหน่งเส้นแบ่งตาม mouse position"""
        if not self.drop_indicator:
            return
        
        # คำนวณว่าจะแสดงเส้นแบ่งด้านบนหรือด้านล่าง
        widget_center = self.height() / 2
        pos = self.pos()
        parent_width = self.parent().width() if self.parent() else self.width()
        
        if mouse_pos.y() < widget_center:
            # แสดงเส้นแบ่งด้านบน
            self.drop_indicator.setGeometry(10, pos.y() - 3, parent_width - 20, 4)
        else:
            # แสดงเส้นแบ่งด้านล่าง
            self.drop_indicator.setGeometry(10, pos.y() + self.height() + 1, parent_width - 20, 4)
    
    def hide_drop_indicator(self):
        """ซ่อนเส้นแบ่งตำแหน่ง drop"""
        if self.drop_indicator:
            self.drop_indicator.hide()
            self.drop_indicator.deleteLater()
            self.drop_indicator = None
    
    def dropEvent(self, event):
        """จัดการ drop event"""
        if self.parent_window:
            source_id = event.mimeData().text().replace("scene_", "")
            source_scene = None
            
            # หา source scene
            for scene in self.parent_window.scenes:
                if str(id(scene)) == source_id:
                    source_scene = scene
                    break
            
            if source_scene and source_scene != self:
                # คำนวณตำแหน่งที่จะ drop ตาม mouse position
                mouse_pos = event.position().toPoint()
                widget_center = self.height() / 2
                drop_before = mouse_pos.y() < widget_center
                
                self.parent_window.reorder_scenes(source_scene, self, drop_before)
                event.acceptProposedAction()
        
        # ซ่อนเส้นแบ่ง
        self.hide_drop_indicator()
    
    def update_summary(self):
        """อัปเดตข้อความสรุปใน header"""
        if not self.form_data:
            self.summary_label.setText("ดับเบิลคลิกเพื่อแก้ไข...")
            return
            
        # สร้างข้อความสรุป
        summary_parts = []
        
        # Scene info
        scene_type = self.form_data.get('scene_type', 'INT.')
        name = self.form_data.get('name', '').strip()
        time_desc = self.form_data.get('time_description', '').strip()
        
        if name:
            summary_parts.append(f"{scene_type} {name}")
            if time_desc:
                summary_parts[-1] += f" - {time_desc}"
        
        # Count content items
        items = self.form_data.get('items', [])
        if items:
            dialog_count = len([item for item in items if item['type'] == 'dialog'])
            action_count = len([item for item in items if item['type'] == 'action'])
            
            counts = []
            if dialog_count > 0:
                counts.append(f"{dialog_count} dialogs")
            if action_count > 0:
                counts.append(f"{action_count} actions")
            
            if counts:
                summary_parts.append(" + ".join(counts))
        
        # Update summary label
        if summary_parts:
            self.summary_label.setText(" | ".join(summary_parts))
        else:
            self.summary_label.setText("ดับเบิลคลิกเพื่อแก้ไข...")

    def delete_scene(self):
        """ลบ scene นี้"""
        if self.parent_window:
            self.parent_window.delete_scene(self)
            
    def update_scene_number(self, number):
        """อัปเดตหมายเลข scene"""
        self.scene_number = number
        self.scene_label.setText(f"SCENE {number}")
    
    def show_context_menu(self, position):
        """แสดง context menu เมื่อคลิกขวา"""
        context_menu = QMenu(self)
        
        # Edit action
        edit_action = QAction("Edit", self)
        edit_action.triggered.connect(self.open_form)
        context_menu.addAction(edit_action)
        
        # Delete action
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete_scene)
        context_menu.addAction(delete_action)
        
        # Duplicate action
        duplicate_action = QAction("Duplicate", self)
        duplicate_action.triggered.connect(self.duplicate_scene)
        context_menu.addAction(duplicate_action)
        
        # แสดง menu ที่ตำแหน่งที่คลิก
        context_menu.exec(self.mapToGlobal(position))
    
    def duplicate_scene(self):
        """สร้างสำเนาของ scene นี้"""
        if self.parent_window:
            self.parent_window.duplicate_scene(self)
        
    def get_scene_data(self):
        """ดึงข้อมูลของ scene นี้"""
        return {
            'scene_number': self.scene_number,
            'scene_type': self.form_data.get('scene_type', 'INT.'),
            'name': self.form_data.get('name', ''),
            'time_description': self.form_data.get('time_description', ''),
            'in_scene': self.form_data.get('in_scene', ''),
            'out_scene': self.form_data.get('out_scene', ''),
            'background': self.form_data.get('background', ''),
            'items': self.form_data.get('items', [])
        }


class LinearScreenplayEditor(QMainWindow):
    """โปรแกรมหลักสำหรับแก้ไข screenplay แบบ linear"""
    
    def __init__(self):
        super().__init__()
        self.scenes = []
        self.setup_ui()
        self.setup_menus()
        
        # เริ่มต้นด้วย scene แรก
        self.add_scene()
        
    def setup_ui(self):
        """สร้าง UI หลัก"""
        self.setWindowTitle("Linear Screenplay Editor")
        self.setGeometry(100, 100, 1000, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Splitter for scenes and preview
        splitter = QSplitter(Qt.Horizontal)
        
        # ปรับแต่ง splitter ให้ใช้งานง่ายขึ้น
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #c0c0c0;
                width: 8px;
                margin: 2px;
                border-radius: 4px;
            }
            QSplitter::handle:hover {
                background-color: #b0b0b0;
                border-color: #666;
            }
            QSplitter::handle:pressed {
                background-color: #999;
                border-color: #333;
            }
            QSplitter::handle:horizontal {
                width: 8px;
                image: url(none);
            }
        """)
        
        # ทำให้ handle เด่นขึ้น
        splitter.setHandleWidth(1)
        splitter.setChildrenCollapsible(False)  # ไม่ให้ panel หายไปเมื่อลากจนสุด
        
        main_layout.addWidget(splitter)
        
        # Left side - Scenes
        scenes_widget = QWidget()
        scenes_widget.setMinimumWidth(300)  # กำหนดความกว้างขั้นต่ำ
        scenes_layout = QVBoxLayout(scenes_widget)
        
        # Add scene button
        add_scene_btn = QPushButton("+ เพิ่ม Scene ใหม่")
        add_scene_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        add_scene_btn.setMaximumWidth(300)
        add_scene_btn.clicked.connect(self.add_scene)
        
        # สร้าง layout สำหรับจัดกึ่งกลาง
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(add_scene_btn)
        button_layout.addStretch()
        
        scenes_layout.addLayout(button_layout)
        
        # Scenes scroll area
        self.scenes_scroll = QScrollArea()
        self.scenes_widget = QWidget()
        self.scenes_layout = QVBoxLayout(self.scenes_widget)
        self.scenes_layout.addStretch()
        
        # ตั้งค่า context menu สำหรับ scenes_widget
        self.scenes_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.scenes_widget.customContextMenuRequested.connect(self.show_scenes_context_menu)
        
        self.scenes_scroll.setWidget(self.scenes_widget)
        self.scenes_scroll.setWidgetResizable(True)
        scenes_layout.addWidget(self.scenes_scroll)
        
        splitter.addWidget(scenes_widget)
        
        # Right side - Preview
        preview_widget = QGroupBox()
        preview_widget.setMinimumWidth(250)  # กำหนดความกว้างขั้นต่ำ
        preview_layout = QVBoxLayout(preview_widget)
        
        # Preview buttons
        preview_btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.update_preview)
        preview_btn_layout.addWidget(refresh_btn)
        
        preview_btn_layout.addStretch()
        preview_layout.addLayout(preview_btn_layout)
        
        # Preview text
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(QFont("Courier", 10))
        preview_layout.addWidget(self.preview_text)
        
        splitter.addWidget(preview_widget)
        
        # ตั้งค่าขนาดเริ่มต้นและอัตราส่วนการ resize
        splitter.setSizes([600, 400])
        splitter.setStretchFactor(0, 1)  # Scenes panel ขยายได้
        splitter.setStretchFactor(1, 1)  # Preview panel ขยายได้เท่าๆ กัน
        
    def setup_menus(self):
        """สร้าง menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        # New
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_screenplay)
        file_menu.addAction(new_action)
        
        # Open
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_screenplay)
        file_menu.addAction(open_action)
        
        # Save
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_screenplay)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # Export menu
        export_menu = file_menu.addMenu("Export")
        
        export_text_action = QAction("Export as Text", self)
        export_text_action.triggered.connect(self.export_as_text)
        export_menu.addAction(export_text_action)
        
        export_pdf_action = QAction("Export as PDF", self)
        export_pdf_action.triggered.connect(self.export_as_pdf)
        export_menu.addAction(export_pdf_action)
        
        export_json_action = QAction("Export as JSON", self)
        export_json_action.triggered.connect(self.export_as_json)
        export_menu.addAction(export_json_action)
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        preview_action = QAction("Update Preview", self)
        preview_action.setShortcut("F5")
        preview_action.triggered.connect(self.update_preview)
        view_menu.addAction(preview_action)
        
    def add_scene(self):
        """เพิ่ม scene ใหม่"""
        scene_number = len(self.scenes) + 1
        scene = ScreenplayScene(scene_number, self)
        
        # Insert before stretch
        self.scenes_layout.insertWidget(self.scenes_layout.count() - 1, scene)
        self.scenes.append(scene)
        
        # Auto scroll to new scene
        self.scenes_scroll.verticalScrollBar().setValue(
            self.scenes_scroll.verticalScrollBar().maximum()
        )
        
        # Update preview
        self.update_preview()
        
    def delete_scene(self, scene):
        """ลบ scene"""
        if len(self.scenes) <= 1:
            QMessageBox.warning(self, "Warning", "ต้องมีอย่างน้อย 1 scene")
            return
            
        self.scenes_layout.removeWidget(scene)
        self.scenes.remove(scene)
        scene.deleteLater()
        
        # Update scene numbers
        self.update_scene_numbers()
        self.update_preview()
    
    def reorder_scenes(self, source_scene, target_scene, drop_before=False):
        """จัดเรียง scene ใหม่โดยการ drag and drop"""
        # หา index ของ source และ target
        source_index = self.scenes.index(source_scene)
        target_index = self.scenes.index(target_scene)
        
        if source_index == target_index:
            return
        
        # ลบ source scene จาก layout และ list
        self.scenes_layout.removeWidget(source_scene)
        self.scenes.pop(source_index)
        
        # คำนวณ position ใหม่สำหรับการ insert
        if drop_before:
            # วางก่อน target scene
            insert_index = target_index if source_index > target_index else target_index - 1
            layout_index = self.scenes_layout.indexOf(target_scene)
        else:
            # วางหลัง target scene
            insert_index = target_index + 1 if source_index > target_index else target_index
            layout_index = self.scenes_layout.indexOf(target_scene) + 1
        
        # ปรับ index ให้อยู่ในขอบเขตที่ถูกต้อง
        insert_index = max(0, min(insert_index, len(self.scenes)))
        
        # Insert ใน list และ layout
        self.scenes.insert(insert_index, source_scene)
        self.scenes_layout.insertWidget(layout_index, source_scene)
        
        # อัปเดตหมายเลข scene ทั้งหมด
        self.update_scene_numbers()
        self.update_preview()
    
    def update_scene_numbers(self):
        """อัปเดตหมายเลข scene ทั้งหมด"""
        for i, scene in enumerate(self.scenes):
            scene.update_scene_number(i + 1)
    
    def duplicate_scene(self, source_scene):
        """สร้างสำเนาของ scene"""
        # หา index ของ scene ต้นฉบับ
        source_index = self.scenes.index(source_scene)
        
        # สร้าง scene ใหม่
        new_scene = ScreenplayScene(source_index + 2, self)  # +2 เพราะจะแทรกหลัง source
        
        # คัดลอกข้อมูลจาก source scene
        new_scene.form_data = source_scene.form_data.copy()
        if 'items' in new_scene.form_data:
            # Deep copy items list
            new_scene.form_data['items'] = [item.copy() for item in source_scene.form_data['items']]
        
        # อัปเดต summary
        new_scene.update_summary()
        
        # แทรก scene ใหม่ลงใน layout และ list
        insert_index = source_index + 1
        layout_insert_index = self.scenes_layout.indexOf(source_scene) + 1
        
        self.scenes.insert(insert_index, new_scene)
        self.scenes_layout.insertWidget(layout_insert_index, new_scene)
        
        # อัปเดตหมายเลข scene ทั้งหมด
        self.update_scene_numbers()
        self.update_preview()
    
    def show_scenes_context_menu(self, position):
        """แสดง context menu สำหรับพื้นที่ scenes"""
        # ตรวจสอบว่าคลิกที่พื้นที่ว่างหรือไม่ (ไม่ใช่ที่ scene widget)
        widget_at_pos = self.scenes_widget.childAt(position)
        if widget_at_pos is None or not isinstance(widget_at_pos.parent(), ScreenplayScene):
            context_menu = QMenu(self.scenes_widget)
            
            # Add scene action
            add_scene_action = QAction("+ เพิ่ม Scene", self)
            add_scene_action.triggered.connect(self.add_scene)
            context_menu.addAction(add_scene_action)
            
            # แสดง menu ที่ตำแหน่งที่คลิก
            context_menu.exec(self.scenes_widget.mapToGlobal(position))
        
    def update_preview(self):
        """อัปเดต preview text"""
        preview_text = "VISUAL NOVEL SCREENPLAY\n"
        preview_text += "=" * 50 + "\n\n"
        preview_text += f"Generated: {time.strftime('%B %d, %Y')}\n\n"
        
        for scene in self.scenes:
            scene_data = scene.get_scene_data()
            
            # In Scene transition
            in_scene = scene_data.get('in_scene', '').strip()
            if in_scene and in_scene != "None":
                preview_text += f"{in_scene}\n\n"
            
            # Scene heading
            name = scene_data.get('name', '').strip()
            if name:
                heading = f"{scene_data['scene_type']} {name}"
                time_desc = scene_data.get('time_description', '').strip()
                if time_desc:
                    heading += f" - {time_desc}"
                preview_text += f"{heading}\n\n"
            
            # Background
            background = scene_data.get('background', '').strip()
            if background:
                preview_text += f"[Background: {background}]\n\n"
            
            # Content
            for item in scene_data['items']:
                if item['type'] == 'dialog':
                    character = item.get('character', '').upper()
                    parentheticals = item.get('parentheticals', '')
                    text = item.get('text', '')
                    
                    if character or text:
                        if character:
                            preview_text += f"                    {character}\n"
                        if parentheticals:
                            preview_text += f"                 ({parentheticals})\n"
                        if text:
                            preview_text += f"              {text}\n"
                        preview_text += "\n"
                        
                elif item['type'] == 'action':
                    text = item.get('text', '')
                    if text:
                        preview_text += f"{text}\n\n"
            
            # Out Scene transition
            out_scene = scene_data.get('out_scene', '').strip()
            if out_scene and out_scene != "None":
                preview_text += f"{out_scene}\n\n"
            
            preview_text += "\n"
        
        preview_text += "                              FADE OUT.\n\n"
        preview_text += "                                END\n"
        
        self.preview_text.setPlainText(preview_text)
        
    def get_all_scenes_data(self):
        """ดึงข้อมูลทั้งหมด"""
        return [scene.get_scene_data() for scene in self.scenes]
        
    def new_screenplay(self):
        """สร้าง screenplay ใหม่"""
        # Clear all scenes
        for scene in self.scenes[:]:
            self.delete_scene(scene)
        
        # Add first scene
        self.add_scene()
        
    def save_screenplay(self):
        """บันทึก screenplay"""
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Screenplay", "", "JSON Files (*.json);;All Files (*)"
        )
        
        if file_name:
            try:
                data = {
                    'title': 'Linear Screenplay',
                    'created': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'scenes': self.get_all_scenes_data()
                }
                
                with open(file_name, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    
                QMessageBox.information(self, "Success", "บันทึกสำเร็จ!")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"เกิดข้อผิดพลาด: {str(e)}")
                
    def open_screenplay(self):
        """เปิด screenplay"""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Screenplay", "", "JSON Files (*.json);;All Files (*)"
        )
        
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Clear existing scenes
                for scene in self.scenes[:]:
                    self.delete_scene(scene)
                
                # Load scenes
                for scene_data in data.get('scenes', []):
                    self.add_scene()
                    scene = self.scenes[-1]
                    
                    # Load data into scene
                    scene.form_data = {
                        'scene_type': scene_data.get('scene_type', 'INT.'),
                        'name': scene_data.get('name', ''),
                        'time_description': scene_data.get('time_description', ''),
                        'in_scene': scene_data.get('in_scene', ''),
                        'out_scene': scene_data.get('out_scene', ''),
                        'background': scene_data.get('background', ''),
                        'items': scene_data.get('items', [])
                    }
                    
                    # Update scene summary
                    scene.update_summary()
                
                self.update_preview()
                QMessageBox.information(self, "Success", "เปิดไฟล์สำเร็จ!")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"เกิดข้อผิดพลาด: {str(e)}")
    
    def export_as_text(self):
        """Export เป็น text file"""
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Export as Text", "screenplay.txt", "Text Files (*.txt);;All Files (*)"
        )
        
        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(self.preview_text.toPlainText())
                QMessageBox.information(self, "Success", "Export สำเร็จ!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"เกิดข้อผิดพลาด: {str(e)}")
    
    def export_as_pdf(self):
        """Export เป็น PDF (ใช้ ExportManager)"""
        QMessageBox.information(self, "PDF Export", "PDF Export ยังไม่รองรับในโหมด Linear Editor\nใช้ Text Export แทน")
    
    def export_as_json(self):
        """Export เป็น JSON"""
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Export as JSON", "screenplay.json", "JSON Files (*.json);;All Files (*)"
        )
        
        if file_name:
            try:
                data = {
                    'title': 'Linear Screenplay Export',
                    'exported': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'scenes': self.get_all_scenes_data()
                }
                
                with open(file_name, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    
                QMessageBox.information(self, "Success", "Export สำเร็จ!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"เกิดข้อผิดพลาด: {str(e)}")


def main():
    """ฟังก์ชันหลัก"""
    app = QApplication(sys.argv)
    app.setApplicationName("Linear Screenplay Editor")
    app.setApplicationVersion("1.0")
    
    window = LinearScreenplayEditor()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
