from PyQt5.QtWidgets import QApplication
from gui import ShapeTrackingApp
import sys

def main():
    app = QApplication(sys.argv)
    ex = ShapeTrackingApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
