import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, \
    QPushButton
import pandas as pd
import pyqtgraph as pg
import seaborn as sns
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from getCrypto import Crypto
import mplcursors



class DateTimeAxis(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        # Convert the tick values to datetime format
        return [pd.to_datetime(value, unit='s').strftime('%Y-%m-%d %H:%M:%S') for value in values]


class MplCanvas(FigureCanvas):

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

        self.init()

        self.get_plot()



    def init(self):

        userLayout = QHBoxLayout()
        current_price = self.cryptoInfo.get_price_now()
        textLayout = QVBoxLayout()
        userName = QLabel("UserName:   " + self.username)
        bitcoinsOwned = QLabel("My bitcoins:   " + str(self.bit) + " BTC")
        walletState = QLabel("My wallet state:   " + str(self.wallet) + " USD")
        currentValue = QLabel("Bitcoin buy price:   " + str(current_price) + " USD")
        bitcoinsValue = QLabel("My Bitcoins value as of now:   " + str(current_price * self.bit) + " USD")

        textLayout.addWidget(userName)
        textLayout.addWidget(bitcoinsOwned)
        textLayout.addWidget(walletState)
        textLayout.addWidget(currentValue)
        textLayout.addWidget(bitcoinsValue)

        # Create the seaborn FigureCanvas object, which defines a single set of axes as self.axes.
        # self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        # toolbar = NavigationToolbar(self.sc, self)
        plot_layout = QVBoxLayout()
        # plot_layout.addWidget(toolbar)
        # plot_layout.addWidget(self.sc)
        # Both alternatives version of changing the background color of the plot area
        sns.set(rc={'axes.facecolor': 'black', 'figure.facecolor': 'black', 'axes.grid': False, 'axes.labelcolor': 'white', 'text.color': 'white', \
                    'xtick.color': 'white', 'ytick.color': 'white', 'axes.edgecolor': 'white', 'axes.titlecolor': 'white'})
        # This with less options
        # plt.style.use("dark_background")
        self.figure = plt.figure()
        # self.figure.set_facecolor("black")
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        plot_layout.addWidget(self.canvas)

        self.figure.canvas.mpl_connect("motion_notify_event", self.hover)

        # Create the buttons and connect them to functions
        buttonLayout = QHBoxLayout()

        button1 = QPushButton("Today")
        button1.clicked.connect(lambda: self.update_request("Daily"))
        buttonLayout.addWidget(button1)

        button2 = QPushButton("Last Week")
        button2.clicked.connect(lambda: self.update_request("Weekly"))
        buttonLayout.addWidget(button2)

        button3 = QPushButton("Last Month")
        button3.clicked.connect(lambda: self.update_request("Monthly"))
        buttonLayout.addWidget(button3)

        button4 = QPushButton("This Year")
        button4.clicked.connect(lambda: self.update_request("this Year"))
        buttonLayout.addWidget(button4)

        button5 = QPushButton("One year")
        button5.clicked.connect(lambda: self.update_request("Yearly"))
        buttonLayout.addWidget(button5)

        # Add the plot layout to the main layout
        # self.layout.addLayout(self.plot_layout)
        userLayout.addLayout(textLayout)
        self.layout.addLayout(userLayout)
        self.layout.addLayout(plot_layout)
        # self.layout.addWidget(self.plot_widget)
        self.layout.addLayout(buttonLayout)
        self.layout.addStretch()

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
        # self.sc.axes.clear()
        self.ax.clear()
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

        # x = [time.timestamp() for time in exchange_rates.index]
        # x = lowPrices.index.astype('int64')//10**9
        x = lowPrices.index
        y = lowPrices.values
        # plot the pandas DataFrame, passing in the matplotlib Canvas axes.
        # TODO
        # sns.set_style("darkgrid")

        self.sc = sns.lineplot(ax=self.ax, x=x, y=y,color = "orange")

        self.ax.tick_params(axis='x', rotation=15)
        # print(x[10])
        # print(lowPrices.index[10])

        # self.min_x, self.max_x = x.min(), x.max()
        # self.min_y,self.max_y = y.min(), y.max()
        self.min_x, self.max_x = pd.to_datetime(x.min().timestamp() * 0.95, unit='s'), pd.to_datetime(
            x.max().timestamp() * 1.05, unit='s')
        self.min_y, self.max_y = y.min() * 0.95, y.max() * 1.05
        self.lnx = plt.plot([x.min(),x.min()], [y.min(), y.min()], color='white', linewidth=0.3)
        self.lny = plt.plot([x.min(),x.max()], [y.min(), y.min()], color='white', linewidth=0.3)
        self.lnx[0].set_linestyle('None')
        self.lny[0].set_linestyle('None')



        # mplcursors.cursor(self.sc, hover=True)
        # exchange_rates.plot(ax=self.sc.axes, y='low')

        # alternatively plot x and y prepared sets of data
        # self.sc.axes.plot(x, y)
        self.canvas.draw()
        # self.sc.draw()
        # Update positions after drawing

    def hover(self, event):
        self.lnx[0].set_data([event.xdata, event.xdata], [self.min_y, self.max_y])
        # print(self.lnx[0].get_data())
        self.lnx[0].set_linestyle('--')
        self.lny[0].set_data([self.min_x,self.max_x], [event.ydata, event.ydata])
        self.lny[0].set_linestyle('--')
        self.canvas.draw()


    def update_request(self, message):

        self.timeStampType = message
        self.get_plot()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PlotWindow()
    window.show()
    sys.exit(app.exec_())

