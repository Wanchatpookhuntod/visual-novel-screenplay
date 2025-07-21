"""
Export utilities for Visual Novel Node Editor
Contains all export functionality: Text, JSON, CSV, PDF
"""

import time
import json
import csv
import os
from PySide6.QtWidgets import QFileDialog, QMessageBox

# PDF generation imports
try:
    from weasyprint import HTML, CSS
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
        """Export connected nodes data as PDF screenplay using WeasyPrint"""
        if not PDF_AVAILABLE:
            QMessageBox.warning(self.main_window, "PDF Export Not Available", 
                              "PDF export requires the 'weasyprint' library.\n\nInstall it with: pip install weasyprint")
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
                
                # Get the path to Sarabun fonts
                sarabun_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Sarabun')
                sarabun_regular = os.path.join(sarabun_path, 'Sarabun-Regular.ttf')
                sarabun_bold = os.path.join(sarabun_path, 'Sarabun-Bold.ttf')
                
                # Create CSS styles for screenplay formatting with Thai font support
                css_content = f"""
                @font-face {{
                    font-family: 'Sarabun';
                    src: url('file://{sarabun_regular}') format('truetype');
                    font-weight: normal;
                    font-style: normal;
                }}
                
                @font-face {{
                    font-family: 'Sarabun';
                    src: url('file://{sarabun_bold}') format('truetype');
                    font-weight: bold;
                    font-style: normal;
                }}
                
                @page {{
                    size: A4;
                    margin: 1in 1in 1in 1.5in;
                }}
                
                body {{
                    font-family: 'Sarabun', 'Noto Sans Thai', 'Arial Unicode MS', sans-serif;
                    font-size: 12pt;
                    line-height: 1.8;
                    color: black;
                    text-rendering: optimizeLegibility;
                    -webkit-font-feature-settings: "liga", "clig";
                    font-feature-settings: "liga", "clig";
                }}
                
                .title {{
                    font-size: 16pt;
                    font-weight: bold;
                    text-align: center;
                    margin-bottom: 30pt;
                    line-height: 1.5;
                }}
                
                .scene-heading {{
                    font-weight: bold;
                    text-transform: uppercase;
                    margin-top: 24pt;
                    margin-bottom: 12pt;
                    line-height: 1.6;
                }}
                
                .character {{
                    font-weight: bold;
                    text-align: center;
                    margin-top: 12pt;
                    margin-bottom: 6pt;
                    margin-left: 2.2in;
                    margin-right: 1in;
                    line-height: 1.6;
                }}
                
                .parenthetical {{
                    text-align: center;
                    margin-bottom: 6pt;
                    margin-left: 2.5in;
                    margin-right: 1.5in;
                    font-style: italic;
                    line-height: 1.6;
                }}
                
                .dialog {{
                    margin-bottom: 12pt;
                    margin-left: 1.5in;
                    margin-right: 1in;
                    line-height: 1.8;
                }}
                
                .action {{
                    margin-bottom: 12pt;
                    margin-top: 6pt;
                    line-height: 1.8;
                }}
                
                .transition {{
                    text-align: right;
                    font-weight: bold;
                    margin-top: 12pt;
                    margin-bottom: 12pt;
                    line-height: 1.6;
                }}
                
                .fade-in {{
                    margin-bottom: 12pt;
                    line-height: 1.6;
                }}
                
                .end {{
                    text-align: center;
                    margin-top: 24pt;
                    line-height: 1.6;
                }}
                
                .spacing {{
                    margin-bottom: 12pt;
                }}
                """
                
                # Create HTML content
                html_content = """
                <!DOCTYPE html>
                <html lang="th">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Visual Novel Screenplay</title>
                </head>
                <body>
                """
                
                # Add title
                html_content += '<div class="title">VISUAL NOVEL SCREENPLAY</div>'
                html_content += f'<p style="text-align: center; margin-bottom: 20pt;">Generated: {time.strftime("%B %d, %Y")}</p>'
                
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
                            html_content += f'<div class="scene-heading">{scene_heading.upper()}</div>'
                            last_scene_location = current_scene_location
                            scene_number += 1
                        
                        # Scene transition IN
                        if in_scene and in_scene != "None":
                            if in_scene == "FADE IN":
                                html_content += '<div class="fade-in">FADE IN:</div>'
                            elif in_scene != "Other":
                                transition_text = self.normalize_thai_text(f"{in_scene}:")
                                html_content += f'<div class="action">{transition_text}</div>'
                        
                        # Background/Setting description
                        if background:
                            background_text = self.normalize_thai_text(background)
                            html_content += f'<div class="action">{background_text}</div>'
                        
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
                                        html_content += f'<div class="character">{character_text}</div>'
                                        
                                        # Parentheticals (if any)
                                        if parentheticals:
                                            parenthetical_text = self.normalize_thai_text(f"({parentheticals})")
                                            html_content += f'<div class="parenthetical">{parenthetical_text}</div>'
                                        
                                        # Dialog text
                                        if text:
                                            dialog_text = self.normalize_thai_text(text)
                                            html_content += f'<div class="dialog">{dialog_text}</div>'
                                
                                elif item['type'] == 'action':
                                    action_text = item.get('text', '')
                                    if action_text:
                                        action_text = self.normalize_thai_text(action_text)
                                        html_content += f'<div class="action">{action_text}</div>'
                        
                        # Scene transition OUT
                        if out_scene and out_scene != "None":
                            if out_scene in ["CUT TO", "DISSOLVE TO", "FADE OUT"]:
                                transition_text = self.normalize_thai_text(f"{out_scene}:")
                                html_content += f'<div class="transition">{transition_text}</div>'
                    
                    # Add spacing between nodes if not the last one
                    if i < len(sequence):
                        html_content += '<div class="spacing"></div>'
                
                # End screenplay
                html_content += '<div class="end">END</div>'
                html_content += '</body></html>'
                
                # Create PDF using WeasyPrint
                html_doc = HTML(string=html_content, base_url='.')
                css_doc = CSS(string=css_content)
                
                html_doc.write_pdf(file_name, stylesheets=[css_doc])
                
                file_size = os.path.getsize(file_name)
                QMessageBox.information(self.main_window, "Export Successful", 
                    f"PDF screenplay exported successfully with WeasyPrint!\n\nFile: {os.path.basename(file_name)}\nScenes: {len(sequence)}\nSize: {file_size/1024:.1f} KB\n\nNote: Enhanced Thai text rendering with proper font support")
                    
            except Exception as e:
                QMessageBox.critical(self.main_window, "Export Error", f"Failed to export PDF:\n{str(e)}")
                import traceback
                traceback.print_exc()
