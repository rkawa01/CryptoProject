import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, \
    QPushButton
import pandas as pd
import pyqtgraph as pg
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from getCrypto import Crypto


class DateTimeAxis(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        # Convert the tick values to datetime format
        return [pd.to_datetime(value, unit='s').strftime('%Y-%m-%d %H:%M:%S') for value in values]


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class PlotWindow(QMainWindow):
    def __init__(self,request = None ,parent=None, username=""):
        super(PlotWindow, self).__init__(parent)
        self.username = username
        self.request = request
        self.timeStampType = None
        self.cryptoInfo = Crypto("BTC", "USD", 2000, "CCCAGG")
        # Get user data
        self.wallet = 0
        self.bit = 0.5
        if self.request and self.request.info:
            self.request.getresponse()
            self.wallet = self.request.info['wallet']
            self.bit = self.request.info['bit']

        # Create a central widget to hold the layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create a vertical layout to hold the plot placeholder and other widgets
        self.layout = QVBoxLayout(self.central_widget)

        self.userLayout = QHBoxLayout()
        current_price = self.cryptoInfo.get_price_now()
        self.textLayout = QVBoxLayout()
        self.label1 = QLabel("UserName:   " + self.username)
        self.bitcoinsOwned = QLabel("My bitcoins:   " + str(self.bit) + " BTC")
        self.walletState = QLabel("My wallet state:   " + str(self.wallet) + " USD")
        self.currentValue = QLabel("Bitcoin buy price:   " + str(current_price) + " USD")
        self.bitcoinsValue = QLabel("My Bitcoins value as of now:   " + str(current_price*self.bit) + " USD")

        self.textLayout.addWidget(self.label1)
        self.textLayout.addWidget(self.bitcoinsOwned)
        self.textLayout.addWidget(self.walletState)
        self.textLayout.addWidget(self.currentValue)
        self.textLayout.addWidget(self.bitcoinsValue)


        # Create the maptlotlib FigureCanvas object, which defines a single set of axes as self.axes.
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        toolbar = NavigationToolbar(self.sc, self)
        self.plot_layout = QVBoxLayout()
        self.plot_layout.addWidget(toolbar)
        self.plot_layout.addWidget(self.sc)

        self.buttonLayout = QHBoxLayout()
        # Create the buttons and connect them to functions
        button1 = QPushButton("Today")
        button1.clicked.connect(lambda: self.update_request("Daily"))
        self.buttonLayout.addWidget(button1)

        button2 = QPushButton("Last Week")
        button2.clicked.connect(lambda: self.update_request("Weekly"))
        self.buttonLayout.addWidget(button2)

        button3 = QPushButton("Last Month")
        button3.clicked.connect(lambda: self.update_request("Monthly"))
        self.buttonLayout.addWidget(button3)

        button4 = QPushButton("This Year")
        button4.clicked.connect(lambda: self.update_request("this Year"))
        self.buttonLayout.addWidget(button4)

        button5 = QPushButton("One year")
        button5.clicked.connect(lambda: self.update_request("Yearly"))
        self.buttonLayout.addWidget(button5)

        # Add the plot layout to the main layout
        # self.layout.addLayout(self.plot_layout)
        self.userLayout.addLayout(self.textLayout)
        self.layout.addLayout(self.userLayout)
        self.layout.addLayout(self.plot_layout)
        # self.layout.addWidget(self.plot_widget)
        self.layout.addLayout(self.buttonLayout)
        self.layout.addStretch()

        self.get_plot()
    def check_textbox(self):

        return True
    def resizeEvent(self, event):
        # Resize the plot placeholder label to be centered in the upper half of the window
        rect = self.geometry()
        plot_height = rect.height() // 2
        plot_width = self.layout.geometry().width()

        # Call the base class resizeEvent to handle any other resizing needed
        super(PlotWindow, self).resizeEvent(event)

    def get_plot(self):
        self.sc.axes.clear()

        # print(self.cryptoInfo.get_price_now())
        exchange_rates = self.cryptoInfo.get_weekly()
        if (self.timeStampType):
            # if you want to retrieve some data from the request

            if self.timeStampType == "Daily":
                exchange_rates = self.cryptoInfo.get_daily()
            elif self.timeStampType == "Weekly":
                exchange_rates = self.cryptoInfo.get_weekly()
            elif self.timeStampType == "Monthly":
                exchange_rates = self.cryptoInfo.get_monthly()
            elif self.timeStampType == "this Year":
                exchange_rates = self.cryptoInfo.get_this_year()
            elif self.timeStampType == "Yearly":
                exchange_rates = self.cryptoInfo.get_yearly()

        keySet = exchange_rates.keys()
        highPrices = exchange_rates.get(keySet[0])
        lowPrices = exchange_rates.get(keySet[1])

        x = [time.timestamp() for time in exchange_rates.index]
        # x = lowPrices.index.astype('int64')//10**9
        y = lowPrices.values

        # plot the pandas DataFrame, passing in the matplotlib Canvas axes.
        exchange_rates.plot(ax=self.sc.axes, y='low')

        # alternatively plot x and y prepared sets of data
        # self.sc.axes.plot(x, y)
        self.sc.draw()

    def update_request(self, message):

        self.timeStampType = message
        self.get_plot()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PlotWindow()
    window.show()
    sys.exit(app.exec_())

