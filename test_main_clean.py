#!/usr/bin/env python3
"""
Test script for main_clean.py with debug output
"""

import sys
import traceback
from PySide6.QtWidgets import QApplication

def main():
    """Test main_clean with debug output"""
    try:
        print("Starting application...")
        
        # Import main_window
        print("Importing main_window...")
        from main_window import MainWindow
        print("main_window imported successfully")
        
        # Create QApplication
        print("Creating QApplication...")
        app = QApplication(sys.argv)
        app.setApplicationName("Visual Novel Node Editor")
        app.setApplicationVersion("2.0")
        app.setOrganizationName("Node Editor Studio")
        print("QApplication created successfully")
        
        # Create main window
        print("Creating MainWindow...")
        window = MainWindow()
        print("MainWindow created successfully")
        
        # Show window
        print("Showing window...")
        window.show()
        print("Window shown successfully")
        
        print("Starting event loop...")
        # Run application
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Error occurred: {e}")
        print("Traceback:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
