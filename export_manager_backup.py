"""
Export # PDF generation imports
try:
    from weasyprint import HTML, CSS
    import unicodedata
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = FalseVisual Novel Node Editor
Contains all export functionality: Text, JSON, CSV, PDF
"""

import time
import json
import csv
import os
from PySide6.QtWidgets import QFileDialog, QMessageBox

# PDF generation imports
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    import unicodedata
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


class ExportManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def get_connected_nodes_sequence(self):
        """Get sequence of connected nodes starting from StartNode"""
        from graphics_items import StartNode
        
        sequence = []
        
        # Find StartNode
        start_node = None
        for node in self.main_window.node_items:
            if isinstance(node, StartNode):
                start_node = node
                break
        
        print(f"Found StartNode: {start_node.name if start_node else 'None'}")
        
        if not start_node:
            return sequence
        
        # Debug: Print all nodes and their connections
        print("=== ALL NODES DEBUG ===")
        for i, node in enumerate(self.main_window.node_items):
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
                for node in self.main_window.node_items:
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
        from graphics_items import NodeScene, StartNode
        
        updated_count = 0
        print("=== UPDATING CONNECTIONS ===")
        for node in self.main_window.node_items:
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
        self.main_window.status_bar.showMessage(f"Updated connection data for {updated_count} nodes", 2000)
        print(f"Updated connection tracking for {updated_count} nodes before export")

    def export_as_text(self):
        """Export connected nodes data as screenplay format"""
        # Update all connection data first
        self.update_all_connections()
        
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self.main_window, "Export as Screenplay", "screenplay.txt", 
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
                
                QMessageBox.information(self.main_window, "Export Successful", 
                    f"Screenplay exported successfully!\n\nFile: {os.path.basename(file_name)}\nScenes: {len(sequence)}")
                    
            except Exception as e:
                QMessageBox.critical(self.main_window, "Export Error", f"Failed to export screenplay:\n{str(e)}")

    def export_as_json(self):
        """Export connected nodes data as structured JSON"""
        # Update all connection data first
        self.update_all_connections()
        
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self.main_window, "Export Node Data as JSON", "node_sequence.json", 
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
                
                from graphics_items import StartNode
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
                QMessageBox.information(self.main_window, "Export Successful", 
                    f"Node sequence exported successfully!\n\nFile: {os.path.basename(file_name)}\nNodes: {len(sequence)}\nSize: {file_size} bytes")
                    
            except Exception as e:
                QMessageBox.critical(self.main_window, "Export Error", f"Failed to export JSON:\n{str(e)}")

    def export_as_csv(self):
        """Export connected nodes data as CSV for spreadsheet analysis"""
        # Update all connection data first
        self.update_all_connections()
        
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self.main_window, "Export Node Data as CSV", "node_sequence.csv", 
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
                    
                    from graphics_items import StartNode
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
                
                QMessageBox.information(self.main_window, "Export Successful", 
                    f"Node sequence exported successfully!\n\nFile: {os.path.basename(file_name)}\nNodes: {len(sequence)}")
                    
            except Exception as e:
                QMessageBox.critical(self.main_window, "Export Error", f"Failed to export CSV:\n{str(e)}")

    def fix_thai_text_advanced(self, text):
        """แก้ไขข้อความภาษาไทยด้วยวิธีที่รุนแรงกว่า"""
        if not text:
            return text
        
        # ใช้ Unicode normalization แบบ NFC
        text = unicodedata.normalize('NFC', text)
        
        # แทนที่คำที่มีปัญหาด้วยการใช้ HTML entities หรือ space
        problematic_words = {
            'ที่': 'ที่',  # เพิ่ม space หลังวรรณยุกต์
            'เพื่อ': 'เพื่อ',
            'ก่อน': 'ก่อน',
            'แล้ว': 'แล้ว',
            'เดือน': 'เดือน',
            'เขียน': 'เขียน',
            'ใหม่': 'ใหม่',
            'ได้': 'ได้',
            'คืน': 'คืน',
            'เมื่อ': 'เมื่อ',
            'ปี่': 'ปี่',
            'กี่': 'กี่'
        }
        
        # แทนที่คำที่มีปัญหา
        for problem_word, fixed_word in problematic_words.items():
            text = text.replace(problem_word, fixed_word)
        
        # วิธีการเพิ่มเติม: แทรก Zero Width Space (ZWSP) หลังวรรณยุกต์
        thai_tone_marks = ['\u0E48', '\u0E49', '\u0E4A', '\u0E4B']  # ่ ้ ๊ ๋
        thai_vowels = ['\u0E34', '\u0E35', '\u0E36', '\u0E37', '\u0E38', '\u0E39', '\u0E31']  # ิ ี ึ ื ุ ู ั
        
        result = ""
        for i, char in enumerate(text):
            result += char
            # เพิ่ม ZWSP หลังวรรณยุกต์
            if char in thai_tone_marks or char in thai_vowels:
                if i < len(text) - 1:  # ไม่ใช่ตัวสุดท้าย
                    result += '\u200B'  # Zero Width Space
        
        return result

    def normalize_thai_text(self, text):
        """ปรับปรุงข้อความภาษาไทยเพื่อแสดงผลวรรณยุกต์ได้ถูกต้อง"""
        if not text:
            return text
        
        # ลองวิธีใหม่ที่รุนแรงกว่า
        return self.fix_thai_text_advanced(text)

    def export_as_pdf(self):
        """Export connected nodes data as PDF screenplay with improved Thai support"""
        if not PDF_AVAILABLE:
            QMessageBox.warning(self.main_window, "PDF Export Not Available", 
                              "PDF export requires the 'reportlab' library.\n\nInstall it with: pip install reportlab")
            return
            
        # Update all connection data first
        self.update_all_connections()
        
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self.main_window, "Export as PDF Screenplay", "screenplay.pdf", 
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
                
                # Register Thai fonts - ลองใช้ฟอนต์ระบบ macOS
                try:
                    # Get the path to Sarabun fonts
                    sarabun_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Sarabun')
                    
                    # ลองฟอนต์ระบบที่รองรับภาษาไทยดี
                    system_fonts = [
                        ('/System/Library/Fonts/Thonburi.ttc', 'Thonburi'),
                        ('/System/Library/Fonts/Krungthep.ttc', 'Krungthep'),
                        ('/Library/Fonts/Ayuthaya.ttf', 'Ayuthaya'),
                        (os.path.join(sarabun_path, 'Sarabun-Regular.ttf'), 'Sarabun'),
                    ]
                    
                    thai_font = 'Helvetica'  # fallback
                    thai_font_bold = 'Helvetica-Bold'
                    
                    for font_path, font_name in system_fonts:
                        if os.path.exists(font_path):
                            try:
                                pdfmetrics.registerFont(TTFont(font_name, font_path, validate=True))
                                pdfmetrics.registerFont(TTFont(f'{font_name}-Bold', font_path, validate=True))
                                thai_font = font_name
                                thai_font_bold = f'{font_name}-Bold'
                                print(f"✅ ใช้ฟอนต์: {font_name} จาก {font_path}")
                                break
                            except:
                                continue
                    
                    if thai_font == 'Helvetica':
                        print("⚠️  ใช้ฟอนต์ Helvetica (fallback)")
                    
                except Exception as e:
                    print(f"❌ ไม่สามารถลงทะเบียนฟอนต์ได้: {e}")
                    thai_font = 'Helvetica'
                    thai_font_bold = 'Helvetica-Bold'
                
                # Define custom styles for screenplay formatting with massive leading for Thai
                styles = getSampleStyleSheet()
                
                # Title style
                title_style = ParagraphStyle('CustomTitle',
                                           parent=styles['Heading1'],
                                           fontSize=16,
                                           fontName=thai_font_bold,
                                           spaceAfter=30,
                                           alignment=TA_CENTER,
                                           leading=24)  # เพิ่มมาก
                
                # Scene heading style
                scene_style = ParagraphStyle('SceneHeading',
                                           parent=styles['Normal'],
                                           fontSize=12,
                                           fontName=thai_font_bold,
                                           spaceAfter=12,
                                           spaceBefore=12,
                                           alignment=TA_LEFT,
                                           leading=20)  # เพิ่มมาก
                
                # Character name style (centered)
                character_style = ParagraphStyle('Character',
                                               parent=styles['Normal'],
                                               fontSize=12,
                                               fontName=thai_font_bold,
                                               spaceAfter=6,
                                               spaceBefore=12,
                                               alignment=TA_CENTER,
                                               leftIndent=2.2*inch,
                                               rightIndent=1*inch,
                                               leading=20)  # เพิ่มมาก
                
                # Parenthetical style
                parenthetical_style = ParagraphStyle('Parenthetical',
                                                   parent=styles['Normal'],
                                                   fontSize=11,
                                                   fontName=thai_font,
                                                   spaceAfter=6,
                                                   alignment=TA_CENTER,
                                                   leftIndent=2.5*inch,
                                                   rightIndent=1.5*inch,
                                                   leading=18)  # เพิ่มมาก
                
                # Dialog style with massive leading for Thai text
                dialog_style = ParagraphStyle('Dialog',
                                            parent=styles['Normal'],
                                            fontSize=12,
                                            fontName=thai_font,
                                            spaceAfter=12,
                                            alignment=TA_LEFT,
                                            leftIndent=1.5*inch,
                                            rightIndent=1*inch,
                                            leading=24)  # เพิ่มมากที่สุด เพื่อให้วรรณยุกต์มีที่เพียงพอ
                
                # Action style with massive leading
                action_style = ParagraphStyle('Action',
                                            parent=styles['Normal'],
                                            fontSize=12,
                                            fontName=thai_font,
                                            spaceAfter=12,
                                            spaceBefore=6,
                                            alignment=TA_LEFT,
                                            leading=24)  # เพิ่มมากที่สุด
                
                # Transition style (right aligned)
                transition_style = ParagraphStyle('Transition',
                                                parent=styles['Normal'],
                                                fontSize=12,
                                                fontName=thai_font_bold,
                                                spaceAfter=12,
                                                spaceBefore=12,
                                                alignment=TA_RIGHT,
                                                leading=20)
                
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
                        scene_type = node.node_data.get('scene_type', 'INT.')
                        name = node.node_data.get('name', '')
                        time_desc = node.node_data.get('time_description', '')
                        in_scene = node.node_data.get('in_scene', '')
                        out_scene = node.node_data.get('out_scene', '')
                        background = node.node_data.get('background', '')
                        
                        # Format scene heading (only if location/time changes)
                        current_scene_location = f"{scene_type} {name}".strip()
                        if current_scene_location != last_scene_location and current_scene_location not in ["INT.", "EXT."]:
                            scene_heading = f"{scene_type} {name}"
                            if time_desc:
                                scene_heading += f" - {time_desc}"
                            # ปรับปรุงข้อความภาษาไทย
                            scene_heading = self.normalize_thai_text(scene_heading)
                            story.append(Paragraph(scene_heading.upper(), scene_style))
                            last_scene_location = current_scene_location
                            scene_number += 1
                        
                        # Scene transition IN
                        if in_scene and in_scene != "None":
                            if in_scene == "FADE IN":
                                story.append(Paragraph("FADE IN:", action_style))
                            elif in_scene != "Other":
                                transition_text = self.normalize_thai_text(f"{in_scene}:")
                                story.append(Paragraph(transition_text, action_style))
                        
                        # Background/Setting description
                        if background:
                            background_text = self.normalize_thai_text(background)
                            story.append(Paragraph(background_text, action_style))
                        
                        # Write screenplay content in order
                        if 'items' in node.node_data and node.node_data['items']:
                            for item in node.node_data['items']:
                                if item['type'] == 'dialog':
                                    character = item.get('character', '').upper()
                                    parentheticals = item.get('parentheticals', '')
                                    text = item.get('text', '')
                                    
                                    if character:
                                        # Character name
                                        character_text = self.normalize_thai_text(character)
                                        story.append(Paragraph(character_text, character_style))
                                        
                                        # Parentheticals (if any)
                                        if parentheticals:
                                            parenthetical_text = self.normalize_thai_text(f"({parentheticals})")
                                            story.append(Paragraph(parenthetical_text, parenthetical_style))
                                        
                                        # Dialog text
                                        if text:
                                            dialog_text = self.normalize_thai_text(text)
                                            story.append(Paragraph(dialog_text, dialog_style))
                                
                                elif item['type'] == 'action':
                                    action_text = item.get('text', '')
                                    if action_text:
                                        action_text = self.normalize_thai_text(action_text)
                                        story.append(Paragraph(action_text, action_style))
                        
                        # Scene transition OUT
                        if out_scene and out_scene != "None":
                            if out_scene in ["CUT TO", "DISSOLVE TO", "FADE OUT"]:
                                transition_text = self.normalize_thai_text(f"{out_scene}:")
                                story.append(Paragraph(transition_text, transition_style))
                    
                    # Add spacing between nodes if not the last one
                    if i < len(sequence):
                        story.append(Spacer(1, 12))
                
                # End screenplay
                story.append(Paragraph("END", ParagraphStyle('End',
                                                           parent=styles['Normal'],
                                                           fontSize=12,
                                                           fontName=thai_font,
                                                           alignment=TA_CENTER,
                                                           leading=16)))
                
                # Build PDF
                doc.build(story)
                
                file_size = os.path.getsize(file_name)
                QMessageBox.information(self.main_window, "Export Successful", 
                    f"PDF screenplay exported successfully!\n\nFile: {os.path.basename(file_name)}\nScenes: {len(sequence)}\nSize: {file_size/1024:.1f} KB\n\nNote: Enhanced Thai text processing applied")
                    
            except Exception as e:
                QMessageBox.critical(self.main_window, "Export Error", f"Failed to export PDF:\n{str(e)}")
                import traceback
                traceback.print_exc()
