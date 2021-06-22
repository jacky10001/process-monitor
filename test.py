from PyQt5 import QtCore, QtGui, QtWidgets
from pyqtgraph import PlotWidget
from PyQt5 import QtCore
import numpy as np
import pyqtgraph as pq


class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # Set the size
        self.resize(600,600)
        # Add PlotWidget control
        self.plotWidget_ted = PlotWidget(self)
        # Set the size and relative position of the control
        self.plotWidget_ted.setGeometry(QtCore.QRect(25,25,550,550))

        # Copy the data in the mode1 code
        # Generate 300 normally distributed random numbers
        self.data1 = np.random.normal(size=300)

        self.curve1 = self.plotWidget_ted.plot(self.data1, name="mode1")

        # Set timer
        self.timer = pq.QtCore.QTimer()
        # Timer signal binding update_data function
        self.timer.timeout.connect(self.update_data)
        # The timer interval is 50ms, which can be understood as refreshing data once in 50ms
        self.timer.start(50)

    # Data shift left
    def update_data(self):
        self.data1[:-1] = self.data1[1:]
        self.data1[-1] = np.random.normal()
        # Data is filled into the drawing curve
        self.curve1.setData(self.data1)


if __name__ == '__main__':
    import sys
    # PyQt5 Program fixed writing
    app = QtWidgets.QApplication(sys.argv)

    # Instantiate and display the window bound to the drawing control
    window = Window()
    window.show()

    # PyQt5 Program fixed writing
    sys.exit(app.exec())