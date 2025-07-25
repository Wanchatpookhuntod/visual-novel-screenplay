"""
Test script for Branch node with dynamic resizing
"""
import sys
from PySide6.QtWidgets import QApplication
from main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    print("=== TESTING DYNAMIC BRANCH NODE ===")
    print("1. Right-click on empty area → Create Branch Node")
    print("2. Branch node starts with 1 output at center")
    print("3. Right-click on Branch node → Add Output")
    print("4. Node should resize and outputs should center")
    print("5. Right-click on Branch node → Remove Output")
    print("6. Node should shrink accordingly")
    print("====================================")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
