from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QScrollArea, QGridLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class ShapeWidget(QWidget):
    def __init__(self, pixmap: QPixmap, shape_id: str, history: list , parent=None) -> None:
        super().__init__(parent)
        self.h_layout = QHBoxLayout()
        self.h_layout.setSpacing(-5)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        
        # icon label
        icon_label = QLabel()
        icon_label.setPixmap(pixmap)
        icon_label.mousePressEvent = lambda event: self.open_window(event, shape_id, history)
        self.h_layout.addWidget(icon_label)
        
        # ID label
        id_label = QLabel(f"ID: {shape_id}")
        id_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        id_label.mousePressEvent = lambda event: self.open_window(event, shape_id, history)
        self.h_layout.addWidget(id_label)
        
    def get_layout(self) -> QHBoxLayout:
        return self.h_layout
    
    def open_window(self, event, shape_id: int, history: list) -> None:
        info_dialog = ShapeInfoDialog(shape_id, history)
        info_dialog.exec_()

class ShapeInfoDialog(QDialog):
    def __init__(self, shape_id: int, history: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f'Shape {shape_id} History')
        
        main_layout = QVBoxLayout(self)

        # scroll area to hold the grid layout
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)

        container_widget = QWidget()
        scroll_area.setWidget(container_widget)
        
        grid_layout = QGridLayout(container_widget)
        container_widget.setLayout(grid_layout)

        # populate the grid layout with the history of the shape
        row = 0
        column = 0
        for frame in history:
            if frame[-1] is not None:
                # Create a label with the frame and value
                label = QLabel(f"Frame {frame[0]}: {frame[1]}")
                grid_layout.addWidget(label, row, column)
                
                # next column
                column += 1
                if column >= 3: 
                    column = 0
                    row += 1

        self.setLayout(main_layout)
