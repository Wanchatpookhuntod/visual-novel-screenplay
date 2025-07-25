"""
Test script for Branch node context menu functionality
"""
import sys
from PySide6.QtWidgets import QApplication
from main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    print("=== TESTING BRANCH NODE ===")
    print("1. Right-click on empty area to create Branch Node")
    print("2. Right-click on Branch Node to see context menu")
    print("3. Try 'Add Output' and 'Remove Output' options")
    print("4. Branch node should start with 1 output")
    print("===============================")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
