"""
Visual Novel Node Editor - Main Entry Point
Clean and organized main application file
"""

import sys
from PySide6.QtWidgets import QApplication
from main_window import MainWindow
from font_manager import font_manager


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Visual Novel Node Editor")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Node Editor Studio")
    
    # Initialize font manager and register fonts for GUI
    try:
        fonts_added = font_manager.register_qt_fonts()
        print(f"Initialized font manager - {fonts_added} fonts added to Qt")
        
        # Show available Thai fonts
        thai_fonts = font_manager.get_available_thai_fonts()
        if thai_fonts:
            print(f"Available Thai fonts: {', '.join(thai_fonts)}")
        else:
            print("No Thai fonts detected in system")
            
    except Exception as e:
        print(f"Font initialization warning: {e}")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
