from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel
)

from PySide6.QtCore import Qt
import sys

class MainView(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Main Window")
        self.setMinimumSize(1200, 800)
        
        
        
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainView()
    window.show()
    sys.exit(app.exec())