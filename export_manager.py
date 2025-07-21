"""
Export utilities for Visual Novel Node Editor
Contains all export functionality: Text, JSON, CSV, PDF
"""

import time
import json
import csv
import os
from PySide6.QtWidgets import QFileDialog, QMessageBox
from font_manager import font_manager

# PDF generation using ReportLab only
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
    print("PDF generation ready using ReportLab")
except ImportError as reportlab_error:
    PDF_AVAILABLE = False
    print(f"ReportLab not available: {reportlab_error}")


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

    def normalize_thai_text(self, text):
        """ปรับปรุงข้อความภาษาไทยเพื่อแสดงผลวรรณยุกต์ได้ถูกต้อง"""
        if not text:
            return text
        
        # ใช้ Unicode normalization แบบ NFC
        text = unicodedata.normalize('NFC', text)
        return text

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

    def export_as_pdf(self):
        """Export connected nodes data as PDF screenplay using ReportLab"""
        if not PDF_AVAILABLE:
            QMessageBox.warning(self.main_window, "PDF Export Not Available", 
                              "PDF export requires the 'reportlab' library.\n\nInstall with: pip install reportlab")
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
                
                # Use ReportLab for PDF generation
                self._export_pdf_reportlab(file_name)
                    
            except Exception as e:
                QMessageBox.critical(self.main_window, "Export Error", f"Failed to export PDF:\n{str(e)}")
                import traceback
                traceback.print_exc()
    
    def _export_pdf_reportlab(self, file_name):
        """Export PDF using ReportLab"""
        sequence = self.get_connected_nodes_sequence()
        
        # Register Thai fonts using font manager
        try:
            fonts_registered = font_manager.register_thai_fonts()
            font_family = font_manager.get_primary_thai_font()
            
            if fonts_registered > 0:
                print(f"Successfully registered {fonts_registered} Thai font variants")
            else:
                print("No Thai fonts found, using system fallback")
        except Exception as e:
            font_family = 'Helvetica'
            print(f"Font registration failed: {e}")
        
        # Create PDF document with screenplay-specific margins for A4
        doc = SimpleDocTemplate(
            file_name, 
            pagesize=A4, 
            topMargin=1*inch, 
            bottomMargin=1*inch,
            leftMargin=1.5*inch,   # Standard screenplay left margin
            rightMargin=1*inch
        )
        story = []
        
        # Screenplay formatting styles for A4 paper
        styles = getSampleStyleSheet()
        
        # Title page style
        title_style = ParagraphStyle(
            'ScreenplayTitle',
            parent=styles['Title'],
            fontName='THSarabunNew-Bold',
            fontSize=18,
            textColor='black',
            alignment=1,  # Center
            spaceAfter=18,
            leading=22,
            bold=True
        )
        
        # Scene heading style (SLUG LINE)
        scene_heading_style = ParagraphStyle(
            'SceneHeading',
            parent=styles['Normal'],
            fontName=font_family,
            fontSize=12,
            textColor='black',
            alignment=0,  # Left
            spaceBefore=12,
            spaceAfter=0,
            leading=14,
            fontWeight='bold'
        )
        
        # Character name style (centered above dialog)
        character_style = ParagraphStyle(
            'Character',
            parent=styles['Normal'],
            fontName=font_family,
            fontSize=12,
            textColor='black',
            alignment=0,  # Left aligned but with specific indentation
            leftIndent=2.2*inch,  # Standard character name position
            spaceBefore=12,
            spaceAfter=0,
            leading=14
        )
        
        # Parentheticals style
        parenthetical_style = ParagraphStyle(
            'Parenthetical',
            parent=styles['Normal'],
            fontName=font_family,
            fontSize=11,
            textColor='black',
            alignment=0,
            leftIndent=1.8*inch,
            rightIndent=2*inch,
            spaceBefore=0,
            spaceAfter=0,
            leading=13
        )
        
        # Dialog style (indented from both sides)
        dialog_style = ParagraphStyle(
            'Dialog',
            parent=styles['Normal'],
            fontName=font_family,
            fontSize=12,
            textColor='black',
            alignment=0,  # Left
            leftIndent=1*inch,    # Dialog indentation
            rightIndent=1.5*inch, # Right margin for dialog
            spaceBefore=0,
            spaceAfter=0,
            leading=16  # Line spacing for Thai text
        )
        
        # Action/Description style (full width)
        action_style = ParagraphStyle(
            'Action',
            parent=styles['Normal'],
            fontName=font_family,
            fontSize=12,
            textColor='black',
            alignment=0,  # Left
            leftIndent=0,
            rightIndent=0,
            spaceBefore=12,
            spaceAfter=0,
            leading=15
        )
        
        # Transition style (left aligned for IN transitions, right aligned for OUT transitions)
        transition_in_style = ParagraphStyle(
            'TransitionIn',
            parent=styles['Normal'],
            fontName=font_family,
            fontSize=12,
            textColor='black',
            alignment=0,  # Left aligned
            spaceAfter=12,
            leading=14
        )
        
        transition_out_style = ParagraphStyle(
            'TransitionOut',
            parent=styles['Normal'],
            fontName=font_family,
            fontSize=12,
            textColor='black',
            alignment=2,  # Right aligned
            spaceBefore=12,
            spaceAfter=6,
            leading=14
        )
        
        # Add title page
        story.append(Paragraph(os.path.splitext(os.path.basename(file_name))[0].upper(), title_style))
        # story.append(Spacer(1, 12))
        story.append(Paragraph(
            f"Writed: {time.strftime('%B %d, %Y')}",
            ParagraphStyle(
            'WrittenDate',
            parent=styles['Normal'],
            fontName=font_family,
            fontSize=12,
            leading=14,
            alignment=2,  # Center
            spaceAfter=0
            )
        ))
        story.append(Spacer(1, 24))  # Page break space
        
        # Process sequence with proper screenplay formatting
        for i, node in enumerate(sequence):
            # Handle IN scene transitions first (before scene heading)
            if hasattr(node, 'node_data') and node.node_data:
                in_scene = node.node_data.get('in_scene', '')
                if in_scene and in_scene != "None" and in_scene != "Other":
                    # Add IN transition before scene heading (left aligned)
                    if in_scene == "FADE IN":
                        story.append(Paragraph("FADE IN:", transition_in_style))
                    elif in_scene in ["CUT IN:", "DISSOLVE IN:", "FADE FROM BLACK:"]:
                        story.append(Paragraph(in_scene, transition_in_style))
                    else:
                        # Custom transition
                        story.append(Paragraph(f"{in_scene.upper()}:", transition_in_style))
            
            # Scene heading (SLUG LINE) - always uppercase
            if hasattr(node, 'node_data') and node.node_data:
                scene_type = node.node_data.get('scene_type', 'INT.')
                scene_name = node.node_data.get('name', node.name)
                time_desc = node.node_data.get('time_description', '')
                # Use running scene number (1-based) for scene_sequence
                sequence_number = i + 1

                # Format scene heading
                scene_heading = f"({sequence_number}) {scene_type.upper()} {scene_name.upper()}"
                if time_desc:
                    scene_heading += f" - {time_desc.upper()}"
                
                story.append(Paragraph(scene_heading, scene_heading_style))
                
                # Skip background/setting description in PDF format
                # (Background is excluded from screenplay PDF as requested)
            else:
                # Fallback scene heading
                story.append(Paragraph(f"SCENE {i+1}: {node.name.upper()}", scene_heading_style))
            
            # Process scene content
            if hasattr(node, 'node_data') and node.node_data and 'items' in node.node_data:
                for item in node.node_data['items']:
                    item_type = item.get('type', '')
                    text = item.get('text', '')
                    
                    if item_type == 'dialog':
                        character = item.get('character', '')
                        parentheticals = item.get('parentheticals', '')
                        
                        # Character name (uppercase, specific indentation)
                        if character:
                            char_text = self.normalize_thai_text(character.upper())
                            story.append(Paragraph(char_text, character_style))
                        
                        # Parentheticals (if any)
                        if parentheticals:
                            paren_text = f"({self.normalize_thai_text(parentheticals)})"
                            story.append(Paragraph(paren_text, parenthetical_style))
                        
                        # Dialog text
                        if text:
                            dialog_text = self.normalize_thai_text(text)
                            story.append(Paragraph(dialog_text, dialog_style))
                    
                    elif item_type == 'action':
                        if text:
                            action_text = self.normalize_thai_text(text)
                            story.append(Paragraph(action_text, action_style))
            
            # Add scene transitions (if specified) - OUT transitions at end of scene
            if hasattr(node, 'node_data') and node.node_data:
                out_scene = node.node_data.get('out_scene', '')
                if out_scene and out_scene != "None" and out_scene != "Other":
                    if out_scene in ["CUT TO:", "DISSOLVE TO:", "FADE OUT:", "FADE TO BLACK:"]:
                        story.append(Paragraph(out_scene, transition_out_style))
                    else:
                        # Custom OUT transition
                        story.append(Paragraph(f"{out_scene.upper()}:", transition_out_style))
            
            # Add spacing between scenes (except for last scene)
            if i < len(sequence) - 1:
                story.append(Spacer(1, 24))
        
        # Final screenplay elements
        story.append(Spacer(1, 24))
        story.append(Paragraph("THE END", title_style))
        
        # Build PDF
        doc.build(story)
        
        file_size = os.path.getsize(file_name)
        QMessageBox.information(self.main_window, "Export Successful", 
            f"Screenplay PDF exported successfully!\n\nFile: {os.path.basename(file_name)}\nScenes: {len(sequence)}\nSize: {file_size/1024:.1f} KB\nFont: {font_family}\nFormat: Standard Screenplay (A4)\n\nNote: Professional screenplay formatting with Thai font support")
