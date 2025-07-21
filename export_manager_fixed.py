"""
Export utilities for Visual Novel Node Editor
Contains all export functionality: Text, JSON, CSV, PDF with fallback support
"""

import time
import json
import csv
import os
from PySide6.QtWidgets import QFileDialog, QMessageBox

# PDF generation imports with fallback
try:
    from weasyprint import HTML, CSS
    import unicodedata
    PDF_AVAILABLE = True
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    WEASYPRINT_AVAILABLE = False
    print(f"WeasyPrint not available: {e}")
    
    # Fallback to ReportLab
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.pdfbase import pdfutils
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfbase import pdfmetrics
        import unicodedata
        PDF_AVAILABLE = True
        print("Using ReportLab as fallback for PDF generation")
    except ImportError as reportlab_error:
        PDF_AVAILABLE = False
        print(f"PDF export not available: {reportlab_error}")


class ExportManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def get_connected_nodes_sequence(self):
        """Build ordered sequence of connected nodes starting from StartNode"""
        sequence = []
        visited = set()
        
        # Find the StartNode
        start_node = None
        for item in self.main_window.scene.items():
            if hasattr(item, 'node_type') and item.node_type == 'StartNode':
                start_node = item
                break
        
        if not start_node:
            return sequence
        
        current_node = start_node
        while current_node and current_node not in visited:
            visited.add(current_node)
            sequence.append(current_node)
            
            # Find next connected node through output
            next_node = None
            output_connected_node = getattr(current_node, 'output_connected_node', None)
            if output_connected_node:
                for item in self.main_window.scene.items():
                    if (hasattr(item, 'title') and 
                        item.title == output_connected_node and 
                        item not in visited):
                        next_node = item
                        break
            
            current_node = next_node
        
        return sequence

    def update_all_connections(self):
        """Update connection tracking for all nodes"""
        print("=== UPDATING CONNECTIONS ===")
        
        for item in self.main_window.scene.items():
            if hasattr(item, 'title') and hasattr(item, 'update_connections'):
                try:
                    old_input = getattr(item, 'input_connected_node', None)
                    old_output = getattr(item, 'output_connected_node', None)
                    
                    item.update_connections()
                    
                    new_input = getattr(item, 'input_connected_node', None)
                    new_output = getattr(item, 'output_connected_node', None)
                    
                    print(f"Updating connections for: {item.title}")
                    print(f"  Input: {old_input} -> {new_input}")
                    print(f"  Output: {old_output} -> {new_output}")
                    
                except Exception as e:
                    print(f"Error updating connections for {getattr(item, 'title', 'Unknown')}: {e}")
        
        print("=== CONNECTION UPDATE COMPLETE ===")

    def normalize_thai_text(self, text):
        """Normalize Thai text for better PDF rendering"""
        if not text:
            return ""
        
        # Unicode normalization
        normalized = unicodedata.normalize('NFC', text)
        
        # Insert Zero Width Non-Joiner (ZWNJ) before tone marks and vowels
        # to prevent incorrect positioning
        import re
        
        # Thai tone marks: ◌่ ◌้ ◌๊ ◌๋
        tone_marks = r'[\u0E48-\u0E4B]'
        
        # Thai vowels that can float: ◌ิ ◌ี ◌ึ ◌ื ◌ุ ◌ู
        vowels = r'[\u0E34-\u0E37\u0E38-\u0E3A]'
        
        # Insert ZWNJ before tone marks and vowels
        normalized = re.sub(f'({vowels})', r'\u200C\1', normalized)
        normalized = re.sub(f'({tone_marks})', r'\u200C\1', normalized)
        
        return normalized

    def export_as_text(self):
        """Export connected nodes data as text file"""
        self.update_all_connections()
        
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self.main_window, "Export as Text", "screenplay.txt", 
            "Text Files (*.txt);;All Files (*)", options=options
        )
        
        if file_name:
            try:
                sequence = self.get_connected_nodes_sequence()
                
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write("VISUAL NOVEL SCREENPLAY\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Total Scenes: {len(sequence)}\n\n")
                    
                    for i, node in enumerate(sequence, 1):
                        f.write(f"SCENE {i}: {node.title}\n")
                        f.write("-" * 30 + "\n")
                        
                        if hasattr(node, 'node_data') and node.node_data:
                            for item in node.node_data:
                                item_type = item.get('type', '')
                                text = item.get('text', '')
                                
                                if item_type == 'character':
                                    character = item.get('character', '')
                                    parentheticals = item.get('parentheticals', '')
                                    
                                    f.write(f"\n{character}")
                                    if parentheticals:
                                        f.write(f" ({parentheticals})")
                                    f.write("\n")
                                    
                                    if text:
                                        f.write(f"{text}\n")
                                
                                elif item_type == 'action':
                                    if text:
                                        f.write(f"\n[{text}]\n")
                        
                        f.write("\n" + "=" * 50 + "\n\n")
                    
                    f.write("END\n")
                
                QMessageBox.information(self.main_window, "Export Successful", 
                    f"Screenplay exported successfully!\n\nFile: {os.path.basename(file_name)}\nScenes: {len(sequence)}")
                    
            except Exception as e:
                QMessageBox.critical(self.main_window, "Export Error", f"Failed to export text:\n{str(e)}")

    def export_as_json(self):
        """Export connected nodes data as JSON file"""
        self.update_all_connections()
        
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self.main_window, "Export as JSON", "nodes.json", 
            "JSON Files (*.json);;All Files (*)", options=options
        )
        
        if file_name:
            try:
                sequence = self.get_connected_nodes_sequence()
                
                export_data = {
                    "metadata": {
                        "export_time": time.strftime('%Y-%m-%d %H:%M:%S'),
                        "total_nodes": len(sequence),
                        "format_version": "2.0"
                    },
                    "nodes": []
                }
                
                for i, node in enumerate(sequence):
                    node_data = {
                        "sequence_number": i + 1,
                        "title": node.title,
                        "type": getattr(node, 'node_type', 'Unknown'),
                        "position": {
                            "x": node.pos().x(),
                            "y": node.pos().y()
                        },
                        "connections": {
                            "input": getattr(node, 'input_connected_node', None),
                            "output": getattr(node, 'output_connected_node', None)
                        }
                    }
                    
                    if hasattr(node, 'node_data') and node.node_data:
                        node_data["content"] = node.node_data
                    
                    export_data["nodes"].append(node_data)
                
                with open(file_name, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(self.main_window, "Export Successful", 
                    f"Node data exported successfully!\n\nFile: {os.path.basename(file_name)}\nNodes: {len(sequence)}")
                    
            except Exception as e:
                QMessageBox.critical(self.main_window, "Export Error", f"Failed to export JSON:\n{str(e)}")

    def export_as_csv(self):
        """Export connected nodes data as CSV file"""
        self.update_all_connections()
        
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self.main_window, "Export as CSV", "nodes.csv", 
            "CSV Files (*.csv);;All Files (*)", options=options
        )
        
        if file_name:
            try:
                sequence = self.get_connected_nodes_sequence()
                
                with open(file_name, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # Header
                    writer.writerow([
                        'Sequence', 'Scene_Title', 'Node_Type', 'Content_Type', 
                        'Character', 'Parentheticals', 'Text', 'Position_X', 'Position_Y'
                    ])
                    
                    # Data rows
                    for i, node in enumerate(sequence, 1):
                        base_row = [
                            i, node.title, getattr(node, 'node_type', 'Unknown'),
                            '', '', '', '', node.pos().x(), node.pos().y()
                        ]
                        
                        if hasattr(node, 'node_data') and node.node_data:
                            for item in node.node_data:
                                row = base_row.copy()
                                row[3] = item.get('type', '')
                                row[4] = item.get('character', '')
                                row[5] = item.get('parentheticals', '')
                                row[6] = item.get('text', '')
                                writer.writerow(row)
                        else:
                            writer.writerow(base_row)
                
                QMessageBox.information(self.main_window, "Export Successful", 
                    f"Node sequence exported successfully!\n\nFile: {os.path.basename(file_name)}\nNodes: {len(sequence)}")
                    
            except Exception as e:
                QMessageBox.critical(self.main_window, "Export Error", f"Failed to export CSV:\n{str(e)}")

    def export_as_pdf(self):
        """Export connected nodes data as PDF screenplay"""
        if not PDF_AVAILABLE:
            QMessageBox.warning(self.main_window, "PDF Export Not Available", 
                              "PDF export requires 'weasyprint' or 'reportlab' library.\n\nInstall with:\npip install weasyprint\nor:\npip install reportlab")
            return
            
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
                
                # Try WeasyPrint first, fallback to ReportLab
                if WEASYPRINT_AVAILABLE:
                    self._export_pdf_weasyprint(file_name)
                else:
                    self._export_pdf_reportlab(file_name)
                    
            except Exception as e:
                QMessageBox.critical(self.main_window, "Export Error", f"Failed to export PDF:\n{str(e)}")
                import traceback
                traceback.print_exc()

    def _export_pdf_reportlab(self, file_name):
        """Export PDF using ReportLab fallback"""
        sequence = self.get_connected_nodes_sequence()
        
        # Try to register Thai fonts
        try:
            sarabun_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Sarabun')
            sarabun_regular = os.path.join(sarabun_path, 'Sarabun-Regular.ttf')
            sarabun_bold = os.path.join(sarabun_path, 'Sarabun-Bold.ttf')
            
            if os.path.exists(sarabun_regular):
                pdfmetrics.registerFont(TTFont('Sarabun', sarabun_regular))
                font_family = 'Sarabun'
            else:
                font_family = 'Helvetica'  # Fallback
        except:
            font_family = 'Helvetica'
        
        # Create PDF document
        doc = SimpleDocTemplate(file_name, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch)
        story = []
        
        # Styles with enhanced leading for Thai text
        styles = getSampleStyleSheet()
        
        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontName=font_family,
            fontSize=16,
            textColor='black',
            alignment=1,  # Center
            spaceAfter=20,
            leading=24
        )
        
        # Character name style
        character_style = ParagraphStyle(
            'Character',
            parent=styles['Normal'],
            fontName=font_family,
            fontSize=12,
            textColor='black',
            alignment=1,  # Center
            spaceBefore=12,
            spaceAfter=6,
            leading=18
        )
        
        # Dialog style
        dialog_style = ParagraphStyle(
            'Dialog',
            parent=styles['Normal'],
            fontName=font_family,
            fontSize=11,
            textColor='black',
            alignment=0,  # Left
            leftIndent=1*inch,
            rightIndent=1*inch,
            spaceBefore=6,
            spaceAfter=12,
            leading=16
        )
        
        # Action style
        action_style = ParagraphStyle(
            'Action',
            parent=styles['Normal'],
            fontName=font_family,
            fontSize=11,
            textColor='black',
            alignment=0,  # Left
            spaceBefore=12,
            spaceAfter=12,
            leading=16
        )
        
        # Add title
        story.append(Paragraph("VISUAL NOVEL SCREENPLAY", title_style))
        story.append(Paragraph(f"Generated: {time.strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Process sequence
        for i, node in enumerate(sequence):
            # Scene header
            scene_title = f"SCENE {i+1}: {node.title}"
            story.append(Paragraph(scene_title, character_style))
            story.append(Spacer(1, 10))
            
            # Node content
            if hasattr(node, 'node_data') and node.node_data:
                for item in node.node_data:
                    item_type = item.get('type', '')
                    text = item.get('text', '')
                    
                    if item_type == 'character':
                        character = item.get('character', '')
                        parentheticals = item.get('parentheticals', '')
                        
                        # Character name
                        char_text = self.normalize_thai_text(character)
                        if parentheticals:
                            char_text += f" ({self.normalize_thai_text(parentheticals)})"
                        story.append(Paragraph(char_text, character_style))
                        
                        # Dialog
                        if text:
                            dialog_text = self.normalize_thai_text(text)
                            story.append(Paragraph(dialog_text, dialog_style))
                    
                    elif item_type == 'action':
                        if text:
                            action_text = self.normalize_thai_text(text)
                            story.append(Paragraph(action_text, action_style))
            
            if i < len(sequence) - 1:
                story.append(Spacer(1, 20))
        
        # Add end
        story.append(Spacer(1, 20))
        story.append(Paragraph("END", character_style))
        
        # Build PDF
        doc.build(story)
        
        file_size = os.path.getsize(file_name)
        QMessageBox.information(self.main_window, "Export Successful", 
            f"PDF screenplay exported successfully with ReportLab!\n\nFile: {os.path.basename(file_name)}\nScenes: {len(sequence)}\nSize: {file_size/1024:.1f} KB\n\nNote: Using ReportLab fallback with enhanced Thai text support")

    def _export_pdf_weasyprint(self, file_name):
        """Export PDF using WeasyPrint (requires system dependencies)"""
        # WeasyPrint implementation would go here
        # For now, fallback to ReportLab
        self._export_pdf_reportlab(file_name)
