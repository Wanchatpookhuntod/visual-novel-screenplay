# Font System Documentation

## Overview
The Visual Novel Node Editor now uses a comprehensive font management system that prioritizes fonts from the local `font/` folder for better Thai text support.

## Font Structure

### Font Folder: `./font/`
- `THSarabunNew.ttf` - Regular weight
- `THSarabunNew Bold.ttf` - Bold weight  
- `THSarabunNew Italic.ttf` - Italic style
- `THSarabunNew BoldItalic.ttf` - Bold Italic style

## Features

### 1. Automatic Font Registration
- Automatically detects and registers all THSarabunNew font variants
- Falls back to system fonts if local fonts are not available
- Registers fonts for both PDF generation (ReportLab) and GUI display (Qt)

### 2. Font Manager (`font_manager.py`)
- Centralized font management system
- Multiple font search paths including system font directories
- Automatic Qt font registration for GUI display
- Thai font detection and listing capabilities

### 3. Enhanced PDF Export
- Uses THSarabunNew fonts for better Thai text rendering with ReportLab
- Improved line spacing and leading for Thai characters
- Support for multiple font weights (regular, bold, italic, bold-italic)
- Unicode normalization for proper diacritic display
- ReportLab-only implementation (WeasyPrint removed)

### 4. System Integration
- Fonts are loaded automatically when the application starts
- Font information is displayed in console for debugging
- Graceful fallback to system fonts if custom fonts fail to load

## Usage

### In Code
```python
from font_manager import font_manager

# Register Thai fonts for PDF
fonts_registered = font_manager.register_thai_fonts()

# Get primary font family name
primary_font = font_manager.get_primary_thai_font()

# Register fonts for Qt GUI
qt_fonts_added = font_manager.register_qt_fonts()

# Get available Thai fonts in system
thai_fonts = font_manager.get_available_thai_fonts()
```

### Font Selection Priority
1. **THSarabunNew** (from `font/` folder) - Primary choice
2. **System Thai fonts** - Secondary choice  
3. **Helvetica** - Fallback for non-Thai text

## Benefits

✅ **Consistent Rendering**: Same fonts used across PDF export and GUI display  
✅ **Better Thai Support**: Optimized fonts for Thai characters and diacritics  
✅ **Portable**: Fonts included with application, no system dependencies  
✅ **Automatic Fallback**: Graceful degradation if fonts are unavailable  
✅ **Multiple Weights**: Support for bold, italic, and bold-italic variants  

## Troubleshooting

### Font Not Loading
- Check if font files exist in `font/` folder
- Verify font file permissions
- Check console output for font registration messages

### Thai Text Display Issues
- Ensure Unicode normalization is working (`normalize_thai_text` function)
- Verify THSarabunNew fonts are properly registered
- Check font metrics and leading settings in PDF styles

### PDF Export Problems
- Confirm ReportLab is installed and working
- Check font registration output in console
- Verify font files are not corrupted

## Technical Details

### Font Registration Process
1. Application starts → `main_clean.py` imports `font_manager`
2. Font manager scans `font/` folder for THSarabunNew variants
3. Fonts are registered with both ReportLab and Qt systems
4. Primary font family is determined and cached
5. Export operations use registered fonts automatically

### File Locations
- Font files: `./font/*.ttf`
- Font manager: `./font_manager.py`
- Export integration: `./export_manager.py`
- Main application: `./main_clean.py`
- Test script: `./test_font_system.py`
