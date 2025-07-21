from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
                                QPushButton, QLabel, QWidget, QFileDialog, QScrollArea, QApplication, QFrame, QComboBox)
from PySide6.QtCore import Qt, QMimeData, QPoint
from PySide6.QtGui import QDrag, QPainter
import json

class DraggableRowWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.drag_start_position = None
        self.form_parent = None
        self.drop_indicator = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if not self.drag_start_position:
            return
        if ((event.position().toPoint() - self.drag_start_position).manhattanLength() < 
            QApplication.startDragDistance()):
            return

        # Start drag operation
        drag = QDrag(self)
        mimeData = QMimeData()
        mimeData.setText(f"row_{id(self)}")
        drag.setMimeData(mimeData)
        
        # Create drag pixmap
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
        if event.mimeData().hasText() and event.mimeData().text().startswith("row_"):
            event.acceptProposedAction()
            self.show_drop_indicator()

    def dragLeaveEvent(self, event):
        self.hide_drop_indicator()
        super().dragLeaveEvent(event)

    def dropEvent(self, event):
        self.hide_drop_indicator()
        if self.form_parent:
            source_id = event.mimeData().text().replace("row_", "")
            source_widget = None
            
            # Find source widget
            for row_data in self.form_parent.rows:
                if str(id(row_data['widget'])) == source_id:
                    source_widget = row_data['widget']
                    break
            
            if source_widget and source_widget != self:
                self.form_parent.reorder_rows(source_widget, self)
                event.acceptProposedAction()

    def show_drop_indicator(self):
        if not self.drop_indicator:
            self.drop_indicator = QFrame(self.parent())
            self.drop_indicator.setFrameStyle(QFrame.HLine)
            self.drop_indicator.setStyleSheet("QFrame { background-color: #007ACC; height: 3px; border: none; margin: 0px; }")
            self.drop_indicator.setFixedHeight(3)
        
        # Position the indicator above this widget
        pos = self.pos()
        parent_width = self.parent().width() if self.parent() else self.width()
        self.drop_indicator.setGeometry(5, pos.y() - 2, parent_width - 10, 3)
        self.drop_indicator.show()
        self.drop_indicator.raise_()

    def hide_drop_indicator(self):
        if self.drop_indicator:
            self.drop_indicator.hide()
            self.drop_indicator.deleteLater()
            self.drop_indicator = None

class MyForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Node Form")
        self.setModal(True)
        self.setMinimumSize(1000, 600)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Scene header layout: INT./EXT. + Name + Time/Description
        scene_layout = QHBoxLayout()
        
        # INT./EXT. dropdown
        self.scene_type_combo = QComboBox()
        self.scene_type_combo.addItems(["INT.", "EXT."])
        self.scene_type_combo.setFixedWidth(80)
        scene_layout.addWidget(self.scene_type_combo)
        
        # Name field
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Scene name")
        scene_layout.addWidget(self.name_input)
        
        # Separator dash label
        dash_label = QLabel("-")
        dash_label.setFixedWidth(15)
        scene_layout.addWidget(dash_label)
        
        # Time/Description field
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("DAY/NIGHT or description")
        scene_layout.addWidget(self.time_input)
        
        main_layout.addLayout(scene_layout)
        
        # In Scene and Out Scene layout
        transition_layout = QHBoxLayout()
        
        # In Scene section
        in_scene_label = QLabel("In Scene:")
        in_scene_label.setFixedWidth(60)
        transition_layout.addWidget(in_scene_label)
        
        self.in_scene_combo = QComboBox()
        self.in_scene_combo.addItems(["None", "FADE IN", "Other"])
        self.in_scene_combo.setFixedWidth(100)
        self.in_scene_combo.currentTextChanged.connect(self.on_in_scene_changed)
        transition_layout.addWidget(self.in_scene_combo)
        
        self.in_scene_text = QLineEdit()
        self.in_scene_text.setPlaceholderText("Custom in scene transition")
        self.in_scene_text.setVisible(False)  # Hidden by default
        transition_layout.addWidget(self.in_scene_text)
        
        # Spacer
        transition_layout.addStretch()
        
        # Out Scene section
        out_scene_label = QLabel("Out Scene:")
        out_scene_label.setFixedWidth(70)
        transition_layout.addWidget(out_scene_label)
        
        self.out_scene_combo = QComboBox()
        self.out_scene_combo.addItems(["None", "CUT TO", "DISSOLVE TO", "FADE OUT", "Other"])
        self.out_scene_combo.setFixedWidth(120)
        self.out_scene_combo.currentTextChanged.connect(self.on_out_scene_changed)
        transition_layout.addWidget(self.out_scene_combo)
        
        self.out_scene_text = QLineEdit()
        self.out_scene_text.setPlaceholderText("Custom out scene transition")
        self.out_scene_text.setVisible(False)  # Hidden by default
        transition_layout.addWidget(self.out_scene_text)
        
        main_layout.addLayout(transition_layout)
        
        # Background field with browse button
        bg_layout = QHBoxLayout()
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)
        bg_layout.addWidget(self.browse_button)
        self.bg_input = QLineEdit()
        bg_layout.addWidget(self.bg_input)
        main_layout.addLayout(bg_layout)
        
        # Add Row button
        button_layout = QHBoxLayout()
        self.add_row_button = QPushButton("Add Row")
        self.add_row_button.setMaximumWidth(150)
        self.add_row_button.setStyleSheet("""
            QPushButton {
                background-color: #0078D4;
                color: white;
                border: 1px solid #005A9E;
                border-radius: 3px;
                padding: 5px 10px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #106EBE;
                border: 1px solid #005A9E;
            }
            QPushButton:pressed {
                background-color: #005A9E;
                border: 1px solid #004578;
            }
        """)
        self.add_row_button.clicked.connect(self.add_row)
        button_layout.addWidget(self.add_row_button)
        
        main_layout.addLayout(button_layout)
        
        # Scroll area for dialog rows
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.dialog_layout = QVBoxLayout(self.scroll_widget)
        self.dialog_layout.setSpacing(5)  # Reduce spacing between rows
        self.dialog_layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins
        self.dialog_layout.addStretch()  # Add stretch at the bottom to push content to top
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        main_layout.addWidget(self.scroll_area)
        
        # Save button (centered)
        save_layout = QHBoxLayout()
        save_layout.addStretch()  # Left spacer
        self.save_button = QPushButton("Save")
        self.save_button.setMinimumWidth(120)
        self.save_button.setMaximumWidth(150)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #0078D4;
                color: white;
                border: 1px solid #005A9E;
                border-radius: 3px;
                padding: 5px 10px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #106EBE;
                border: 1px solid #005A9E;
            }
            QPushButton:pressed {
                background-color: #005A9E;
                border: 1px solid #004578;
            }
        """)
        self.save_button.clicked.connect(self.save_data)
        save_layout.addWidget(self.save_button)
        save_layout.addStretch()  # Right spacer
        main_layout.addLayout(save_layout)
        
        self.setLayout(main_layout)
        
        # All rows list (both dialog and action)
        self.rows = []
        # Drop indicator for visual feedback
        self.drop_indicators = []

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Background Image", 
            "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.bg_input.setText(file_path)

    def on_in_scene_changed(self, text):
        """Show/hide in scene text input based on selection"""
        if text == "Other":
            self.in_scene_text.setVisible(True)
            self.in_scene_text.setPlaceholderText("Enter custom in scene transition")
        else:
            self.in_scene_text.setVisible(False)
            self.in_scene_text.clear()

    def on_out_scene_changed(self, text):
        """Show/hide out scene text input based on selection"""
        if text == "Other":
            self.out_scene_text.setVisible(True)
            self.out_scene_text.setPlaceholderText("Enter custom out scene transition")
        else:
            self.out_scene_text.setVisible(False)
            self.out_scene_text.clear()

    def add_row(self):
        """Add a new row with type dropdown"""
        row_widget = DraggableRowWidget()
        row_widget.form_parent = self
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(5, 2, 5, 2)
        row_layout.setSpacing(5)
        
        # Row number label
        number_label = QLabel("1")
        number_label.setFixedWidth(30)
        number_label.setStyleSheet("QLabel { font-weight: bold; color: #0066CC; text-align: center; }")
        row_layout.addWidget(number_label)
        
        # Type dropdown
        type_combo = QComboBox()
        type_combo.addItems(["Dialog", "Action"])
        type_combo.setFixedWidth(80)
        type_combo.currentTextChanged.connect(lambda text: self.on_type_changed(row_widget, text))
        row_layout.addWidget(type_combo)
        
        # Character name input (initially visible for dialog)
        character_input = QLineEdit()
        character_input.setPlaceholderText("Character name")
        row_layout.addWidget(character_input, 1)
        
        # Parentheticals input (initially visible for dialog)
        parentheticals_input = QLineEdit()
        parentheticals_input.setPlaceholderText("(action/emotion)")
        row_layout.addWidget(parentheticals_input, 1)
        
        # Dialog/Action text input
        text_input = QLineEdit()
        text_input.setPlaceholderText("Dialog text")
        row_layout.addWidget(text_input, 3)
        
        # Remove button
        remove_button = QPushButton("✕")
        remove_button.setFixedWidth(40)
        remove_button.setToolTip("Remove row")
        remove_button.clicked.connect(lambda: self.remove_row(row_widget))
        row_layout.addWidget(remove_button)
        
        # Add to layout and list
        self.dialog_layout.insertWidget(self.dialog_layout.count() - 1, row_widget)
        self.rows.append({
            'widget': row_widget,
            'type_combo': type_combo,
            'character': character_input,
            'parentheticals': parentheticals_input,
            'text': text_input,
            'number_label': number_label,
            'type': 'Dialog'  # Default type
        })
        
        self.update_row_numbers()

    def on_type_changed(self, row_widget, row_type):
        """Handle row type change"""
        # Find the row data
        row_data = None
        for r in self.rows:
            if r['widget'] == row_widget:
                row_data = r
                break
        
        if not row_data:
            return
            
        row_data['type'] = row_type
        
        if row_type == "Dialog":
            # Show character and parentheticals fields
            row_data['character'].setVisible(True)
            row_data['parentheticals'].setVisible(True)
            row_data['text'].setPlaceholderText("Dialog text")
            row_data['number_label'].setStyleSheet("QLabel { font-weight: bold; color: #0066CC; text-align: center; }")
        else:  # Action
            # Hide character and parentheticals fields
            row_data['character'].setVisible(False)
            row_data['parentheticals'].setVisible(False)
            row_data['text'].setPlaceholderText("Action text (e.g., 'Character walks to door', 'Sound plays')")
            row_data['number_label'].setStyleSheet("QLabel { font-weight: bold; color: #CC6600; text-align: center; }")
        
        self.update_row_numbers()

    def remove_row(self, row_widget):
        """Remove a row"""
        for i, row_data in enumerate(self.rows):
            if row_data['widget'] == row_widget:
                self.dialog_layout.removeWidget(row_widget)
                row_widget.deleteLater()
                self.rows.pop(i)
                break
        
        self.update_row_numbers()

    def reorder_rows(self, source_widget, target_widget):
        # Hide all drop indicators
        self.hide_all_drop_indicators()
        
        # Get current layout positions
        source_layout_pos = self._get_layout_index(source_widget)
        target_layout_pos = self._get_layout_index(target_widget)
        
        if source_layout_pos != -1 and target_layout_pos != -1 and source_layout_pos != target_layout_pos:
            # Remove source widget from layout
            self.dialog_layout.removeWidget(source_widget)
            
            # Recalculate target position after removal
            new_target_layout_pos = self._get_layout_index(target_widget)
            
            # Determine where to insert based on drag direction
            if source_layout_pos < target_layout_pos:
                # Moving down: insert after target
                insert_pos = new_target_layout_pos + 1
            else:
                # Moving up: insert before target
                insert_pos = new_target_layout_pos
            
            # Re-add source widget at new position
            self.dialog_layout.insertWidget(insert_pos, source_widget)
            
            # Update row numbers
            self.update_row_numbers()

    def hide_all_drop_indicators(self):
        """Hide all drop indicators"""
        for row_data in self.rows:
            if hasattr(row_data['widget'], 'hide_drop_indicator'):
                row_data['widget'].hide_drop_indicator()

    def _get_layout_index(self, widget):
        """Get the index of a widget in the layout"""
        for i in range(self.dialog_layout.count()):
            if self.dialog_layout.itemAt(i).widget() == widget:
                return i
        return -1

    def update_row_numbers(self):
        # Get all rows in layout order and assign sequential numbers
        all_widgets = []
        for i in range(self.dialog_layout.count()):
            widget = self.dialog_layout.itemAt(i).widget()
            if widget:
                all_widgets.append(widget)
        
        # Assign sequential numbers to all rows
        row_number = 1
        for widget in all_widgets:
            # Find if this widget is in our rows list
            for row_data in self.rows:
                if row_data['widget'] == widget:
                    row_type = row_data['type']
                    if row_type == "Dialog":
                        row_data['number_label'].setText(f"D{row_number}")
                        row_data['number_label'].setStyleSheet("QLabel { font-weight: bold; color: #0066CC; text-align: center; }")
                    else:  # Action
                        row_data['number_label'].setText(f"A{row_number}")
                        row_data['number_label'].setStyleSheet("QLabel { font-weight: bold; color: #CC6600; text-align: center; }")
                    row_number += 1
                    break

    def get_form_data(self):
        """Get all form data as dictionary in layout order"""
        # Collect all data in layout order
        data = {
            'scene_type': self.scene_type_combo.currentText(),
            'name': self.name_input.text(),
            'time_description': self.time_input.text(),
            'in_scene': self.in_scene_combo.currentText() if self.in_scene_combo.currentText() not in ["None", "Other"] else self.in_scene_text.text(),
            'out_scene': self.out_scene_combo.currentText() if self.out_scene_combo.currentText() not in ["None", "Other"] else self.out_scene_text.text(),
            'background': self.bg_input.text(),
            'items': [],  # Mixed dialogs and actions in order
        }
        
        # Get all widgets in layout order
        for i in range(self.dialog_layout.count()):
            widget = self.dialog_layout.itemAt(i).widget()
            if widget:
                # Check if this widget is in our rows
                for row_data in self.rows:
                    if row_data['widget'] == widget:
                        row_type = row_data['type']
                        text_content = row_data['text'].text()
                        
                        if row_type == "Dialog":
                            character = row_data['character'].text()
                            parentheticals = row_data['parentheticals'].text()
                            if character or parentheticals or text_content:  # Only save non-empty rows
                                item = {
                                    'type': 'dialog',
                                    'order': i + 1,
                                    'character': character,
                                    'parentheticals': parentheticals,
                                    'text': text_content
                                }
                                data['items'].append(item)
                        else:  # Action
                            if text_content:  # Only save non-empty action rows
                                item = {
                                    'type': 'action',
                                    'order': i + 1,
                                    'text': text_content
                                }
                                data['items'].append(item)
                        break
        
        return data

    def clear_all_rows(self):
        """Clear all existing rows in the form"""
        # Remove all existing rows from the layout and list
        for row in self.rows[:]:  # Create a copy to avoid modification during iteration
            self.remove_row(row['widget'])
        
        # Clear the rows list
        self.rows = []
        
        # Update row numbers after clearing
        self.update_row_numbers()

    def save_data(self):
        """Close dialog and return data"""
        self.accept()

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    form = MyForm()

    form.show()

    if form.exec() == QDialog.Accepted:
        data = form.get_form_data()
        print(data)

    sys.exit(0)
