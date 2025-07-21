"""
Visual Novel Node Editor - Main Entry Point
Clean and organized main application file
"""

import sys
from PySide6.QtWidgets import QApplication
from main_window import MainWindow


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Visual Novel Node Editor")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Node Editor Studio")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
