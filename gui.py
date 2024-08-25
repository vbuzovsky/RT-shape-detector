from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy, QGridLayout, QFrame, QFileDialog, QSpacerItem
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QBrush
from PyQt5.QtCore import Qt
from video_processor import VideoProcessorWorker
from shape_info_ui import ShapeWidget
import numpy as np

class ShapeTrackingApp(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.initUI()
        self.setFixedWidth(1340)
        self.worker = None
        self.video_file = None

    def initUI(self) -> None:
        self.setWindowTitle('Shape Tracking')
        main_layout = QVBoxLayout(self)

        # top_layout -> two windows (frame display and path drawing)
        top_layout = QHBoxLayout()

        # downscaled sizes for the windows
        window_width = 640
        window_height = 360

        # left window for frame display
        self.frame_label = QLabel(self)
        self.frame_label.setFixedSize(window_width, window_height)
        self.frame_label.setScaledContents(True)

        black_frame_image = self.create_black_image(window_height, window_width)
        self.frame_label.setPixmap(black_frame_image)
        top_layout.addWidget(self.frame_label, 1)

        # right window for path drawing
        self.image_label = QLabel(self)
        self.image_label.setFixedSize(window_width, window_height)
        self.image_label.setScaledContents(True)

        black_path_image = self.create_black_image(window_height, window_width)
        self.image_label.setPixmap(black_path_image)
        top_layout.addWidget(self.image_label, 1)

        # left (buttons), right (shape list)
        bottom_layout = QHBoxLayout()

        # left (buttons)
        left_layout = QVBoxLayout()

        # HBox for buttons (Select File, Start)
        button_layout = QHBoxLayout()
        self.select_file_button = QPushButton('Select File', self)
        self.select_file_button.clicked.connect(self.select_file)
        button_layout.addWidget(self.select_file_button)

        self.start_button = QPushButton('Start', self)
        self.start_button.setEnabled(False)  # Disabled until file is selected
        self.start_button.clicked.connect(self.start_processing)
        button_layout.addWidget(self.start_button)
        button_layout.setAlignment(Qt.AlignTop)

        left_layout.addLayout(button_layout)
        bottom_layout.addLayout(left_layout, 1)  

        # right (shape list)
        right_layout = QVBoxLayout()
        self.grid_layout = QGridLayout()
        right_layout.addLayout(self.grid_layout)

        # ensure equal splitting
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        right_layout.addSpacerItem(spacer)
        bottom_layout.addLayout(right_layout, 1)  

        main_layout.addLayout(top_layout, 7)
        main_layout.addLayout(bottom_layout, 3)

        self.setLayout(main_layout) 

    def select_file(self) -> None:
        """Open a file dialog to select a video file."""
        options = QFileDialog.Options()
        file, _ = QFileDialog.getOpenFileName(self, "Select Video File", "",
                                              "Video Files (*.mp4 *.avi *.mov);;All Files (*)", options=options)
        if file:
            self.video_file = file
            self.start_button.setEnabled(True)

    def start_processing(self) -> None:
        """Start the VideoProcessorWorker to process the video file."""
        if not self.video_file:
            return # no file selected

        self.start_button.setEnabled(False)
        self.worker = VideoProcessorWorker(self.video_file) 

        # connect signals with VideoProcessor worker
        self.worker.shapes_updated.connect(self.update_shape_list)
        self.worker.image_updated.connect(self.update_image)  
        self.worker.frame_updated.connect(self.update_frame) 
        self.worker.processing_finished.connect(self.on_processing_finished)
        self.worker.start()

    def update_shape_list(self, tracked_shapes: list) -> None:
        for i in reversed(range(self.grid_layout.count())): # clear the grid layout
            self.grid_layout.itemAt(i).widget().setParent(None)

        for index, shape in enumerate(tracked_shapes):
            # pixmap for the shape image
            pixmap_size = 30
            pixmap = QPixmap(pixmap_size, pixmap_size)
            pixmap.fill(QColor('transparent'))

            painter = QPainter(pixmap)
            painter.setBrush(QBrush(QColor(*shape.color)))
            painter.setPen(QColor(*shape.color))

            if shape.shape_type.name == "CIRCLE":
                painter.drawEllipse(0, 0, pixmap_size-5, pixmap_size-5)
            else:
                painter.drawRect(0, 0, pixmap_size-5, pixmap_size-5)

            painter.end()

            # one shape item (icon + ID), wrapped in a container
            h_layout = ShapeWidget(pixmap, str(shape.id), shape.history).get_layout()
            container = QFrame()
            container.setLayout(h_layout)

            # add the container to the grid layout
            row = index // 6  # calc row number (6 items per row)
            col = index % 6  
            self.grid_layout.addWidget(container, row, col)

    def update_image(self, qimage: QImage) -> None:
        pixmap = QPixmap.fromImage(qimage)
        self.image_label.setPixmap(pixmap)

    def update_frame(self, qimage: QImage) -> None:
        pixmap = QPixmap.fromImage(qimage)
        self.frame_label.setPixmap(pixmap)

    def on_processing_finished(self) -> None:
        self.start_button.setEnabled(True)

    def create_black_image(self, height: int, width: int) -> QPixmap:
        black_image = np.zeros((height, width, 3), dtype=np.uint8)
        qimage = QImage(black_image.data, width, height, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        return pixmap

