"""
Debug script to test input circle positioning in branch nodes
"""
import sys
from PySide6.QtWidgets import QApplication
from main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    print("=== DEBUG: INPUT CIRCLE POSITIONING ===")
    print("1. Create a Branch node")
    print("2. Check if input circle is at center")
    print("3. Add outputs and check if input stays centered")
    print("=======================================")
    
    # Create a test branch node programmatically
    from graphics_items import BranchNode
    
    # Get the scene from main window
    scene = window.graphics_view.scene()
    
    # Create test branch node
    test_node = BranchNode(100, 100)
    scene.addItem(test_node)
    window.node_items.append(test_node)
    
    print(f"Initial node height: {test_node.rect().height()}")
    print(f"Initial input circle position: {test_node.input_circle.rect()}")
    print(f"Expected center_y: {test_node.rect().height() / 2}")
    
    # Add some outputs to test
    test_node.add_output_circle()
    print(f"After 1 add - node height: {test_node.rect().height()}")
    print(f"After 1 add - input circle position: {test_node.input_circle.rect()}")
    print(f"After 1 add - expected center_y: {test_node.rect().height() / 2}")
    
    test_node.add_output_circle()
    print(f"After 2 add - node height: {test_node.rect().height()}")
    print(f"After 2 add - input circle position: {test_node.input_circle.rect()}")
    print(f"After 2 add - expected center_y: {test_node.rect().height() / 2}")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
