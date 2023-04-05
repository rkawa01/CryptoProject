import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QBrush, QColor, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QSizePolicy, QWidget, QHBoxLayout, QVBoxLayout, QLabel


class PlotWindow(QMainWindow):
    def __init__(self, parent=None):
        super(PlotWindow, self).__init__(parent)

        # Create a central widget to hold the layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create a vertical layout to hold the plot placeholder and other widgets
        self.layout = QVBoxLayout(self.central_widget)

        # Create a layout for the plot placeholder
        self.plot_layout = QHBoxLayout()

        # Create a label for the placeholder
        self.plot_label = QLabel(self.central_widget)
        self.plot_label.setText("Plot Placeholder")
        self.plot_label.setAlignment(Qt.AlignCenter)

        # Set the font for the label
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        self.plot_label.setFont(font)

        # Set the background color for the label
        self.plot_label.setAutoFillBackground(True)
        palette = self.plot_label.palette()
        palette.setColor(self.plot_label.backgroundRole(), QColor(0, 0, 255))
        self.plot_label.setPalette(palette)

        # Set the size policy for the label so it fills the available space
        self.plot_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add the label to the plot layout
        self.plot_layout.addStretch()
        self.plot_layout.addWidget(self.plot_label)
        self.plot_layout.addStretch()

        # Add the plot layout to the main layout
        self.layout.addLayout(self.plot_layout)
        self.layout.addStretch()

    def resizeEvent(self, event):
        # Resize the plot placeholder label to be centered in the upper half of the window
        rect = self.geometry()
        plot_height = rect.height() // 2
        plot_width = self.plot_layout.geometry().width()
        self.plot_label.setFixedHeight(plot_height)
        self.plot_layout.setContentsMargins((rect.width() - plot_width) // 2, plot_height // 2, 0, 0)

        # Call the base class resizeEvent to handle any other resizing needed
        super(PlotWindow, self).resizeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PlotWindow()
    window.show()
    sys.exit(app.exec_())
