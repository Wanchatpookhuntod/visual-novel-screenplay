"""
Font Manager for Visual Novel Node Editor
Handles Thai font registration and management
"""

import os
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from PySide6.QtCore import QStandardPaths
from PySide6.QtGui import QFontDatabase


class FontManager:
    """Manages font registration for the application"""
    
    def __init__(self):
        self.registered_fonts = {}
        self.font_paths = []
        self._setup_font_paths()
    
    def _setup_font_paths(self):
        """Setup font search paths"""
        # Application font folder
        app_font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'font')
        if os.path.exists(app_font_path):
            self.font_paths.append(app_font_path)
        
        # System font paths
        system_font_paths = [
            os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts'),
            QStandardPaths.standardLocations(QStandardPaths.FontsLocation)
        ]
        
        for path_list in system_font_paths:
            if isinstance(path_list, list):
                self.font_paths.extend(path_list)
            elif isinstance(path_list, str) and os.path.exists(path_list):
                self.font_paths.append(path_list)
    
    def register_thai_fonts(self):
        """Register Thai fonts for PDF generation"""
        fonts_registered = 0
        
        # THSarabunNew fonts from font folder
        thsarabun_fonts = {
            'THSarabunNew': 'THSarabunNew.ttf',
            'THSarabunNew-Bold': 'THSarabunNew Bold.ttf',
            'THSarabunNew-Italic': 'THSarabunNew Italic.ttf',
            'THSarabunNew-BoldItalic': 'THSarabunNew BoldItalic.ttf'
        }
        
        for font_name, font_file in thsarabun_fonts.items():
            font_path = self._find_font_file(font_file)
            if font_path:
                try:
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    self.registered_fonts[font_name] = font_path
                    fonts_registered += 1
                    print(f"Registered font: {font_name} from {font_path}")
                except Exception as e:
                    print(f"Failed to register {font_name}: {e}")
        
        return fonts_registered
    
    def _find_font_file(self, font_filename):
        """Find font file in search paths"""
        for font_path in self.font_paths:
            full_path = os.path.join(font_path, font_filename)
            if os.path.exists(full_path):
                return full_path
        return None
    
    def get_primary_thai_font(self):
        """Get the primary Thai font family name"""
        if 'THSarabunNew' in self.registered_fonts:
            return 'THSarabunNew'
        return 'Helvetica'  # Fallback
    
    def register_qt_fonts(self):
        """Register fonts with Qt for GUI display"""
        font_db = QFontDatabase()
        fonts_added = 0
        
        # Add fonts from font folder to Qt
        font_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'font')
        if os.path.exists(font_folder):
            for font_file in os.listdir(font_folder):
                if font_file.endswith('.ttf'):
                    font_path = os.path.join(font_folder, font_file)
                    font_id = font_db.addApplicationFont(font_path)
                    if font_id != -1:
                        families = font_db.applicationFontFamilies(font_id)
                        fonts_added += 1
                        print(f"Added Qt font: {', '.join(families)} from {font_file}")
        
        return fonts_added
    
    def get_available_thai_fonts(self):
        """Get list of available Thai font families"""
        font_db = QFontDatabase()
        all_families = font_db.families()
        
        thai_fonts = []
        thai_keywords = ['sarabun', 'tahoma', 'cordia', 'angsana', 'browallia', 'th']
        
        for family in all_families:
            if any(keyword in family.lower() for keyword in thai_keywords):
                thai_fonts.append(family)
        
        return thai_fonts


# Global font manager instance
font_manager = FontManager()
