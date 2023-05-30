import sys

from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, \
    QPushButton, QLineEdit, QDoubleSpinBox
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
from time import sleep


class DateTimeAxis(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        # Convert the tick values to datetime format
        return [pd.to_datetime(value, unit='s').strftime('%Y-%m-%d %H:%M:%S') for value in values]


class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class Worker(QObject):
    finished = pyqtSignal()
    update = pyqtSignal()

    def run(self):
#         Constant update
        while True:
            self.update.emit()
            sleep(60)
        self.finished.emit()


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

        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.update.connect(self.update_runtime)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Create a central widget to hold the layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create a vertical layout to hold the plot placeholder and other widgets
        self.layout = QVBoxLayout(self.central_widget)

        self.init()

        self.get_plot()

        # Comment to eventually not run the thread
        # self.thread.start()

    def init(self):

        userLayout = QHBoxLayout()
        textLayout = QVBoxLayout()
        current_price = self.cryptoInfo.get_price_now()
        self.userName = QLabel("UserName:   " + self.username)
        self.bitcoinsOwned = QLabel("My bitcoins:   " + str(self.bit) + " BTC")
        self.walletState = QLabel("My wallet state:   " + str(self.wallet) + " USD")
        self.currentValue = QLabel("Bitcoin buy price:   " + str(current_price) + " USD")
        self.bitcoinsValue = QLabel("My Bitcoins value as of now:   " + str(current_price * self.bit) + " USD")

        textLayout.addWidget(self.userName)
        textLayout.addWidget(self.bitcoinsOwned)
        textLayout.addWidget(self.walletState)
        textLayout.addWidget(self.currentValue)
        textLayout.addWidget(self.bitcoinsValue)

        buySellLayout = QVBoxLayout()
        buyLayout = QHBoxLayout()
        sellLayout = QHBoxLayout()

        self.buySpinBox = QDoubleSpinBox()
        self.buySpinBox.setMaximum(self.wallet / current_price)
        self.sellSpinBox = QDoubleSpinBox()
        self.sellSpinBox.setMaximum(self.bit)

        buyButton = QPushButton("Buy")
        buyButton.clicked.connect(lambda: self.buy(self.buySpinBox))
        sellButton = QPushButton("Sell")
        sellButton.clicked.connect(lambda: self.sell(self.sellSpinBox))


        buyLayout.addWidget(self.buySpinBox)
        sellLayout.addWidget(self.sellSpinBox)
        buyLayout.addWidget(buyButton)
        sellLayout.addWidget(sellButton)
        buySellLayout.addLayout(buyLayout)
        buySellLayout.addLayout(sellLayout)




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
        userLayout.addLayout(buySellLayout)
        self.layout.addLayout(userLayout)
        self.layout.addLayout(plot_layout)
        # self.layout.addWidget(self.plot_widget)
        self.layout.addLayout(buttonLayout)
        self.layout.addStretch()

    def buy(self,spinBox):
        self.bit += spinBox.value()
        self.wallet -= self.cryptoInfo.get_price_now() * spinBox.value()
        self.update_labels()
    def sell(self,spinBox):
        self.bit -= spinBox.value()
        self.wallet += self.cryptoInfo.get_price_now() * spinBox.value()
        self.update_labels()
    def update_labels(self):
        self.sellSpinBox.setMaximum(self.bit)
        self.buySpinBox.setMaximum(self.wallet / self.cryptoInfo.get_price_now())
        self.bitcoinsOwned.setText("My bitcoins:   " + str(self.bit) + " BTC")
        self.walletState.setText("My wallet state:   " + str(self.wallet) + " USD")
        self.bitcoinsValue.setText("My Bitcoins value as of now:   " + str(self.cryptoInfo.get_price_now() * self.bit) + " USD")
    def update_runtime(self):
        self.bitcoinsValue.setText("My Bitcoins value as of now:   " + str(self.cryptoInfo.get_price_now() * self.bit) + " USD")
        self.currentValue.setText("Bitcoin buy price:   " + str(self.cryptoInfo.get_price_now()) + " USD")
        self.get_plot()
    def update_request(self, message):
        self.timeStampType = message
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

        self.ax.clear()

        self.exchange_rates = self.cryptoInfo.get_weekly()
        if (self.timeStampType):
            # if you want to retrieve some data from the request

            if self.timeStampType == "Daily":
                self.exchange_rates = self.cryptoInfo.get_daily()
            elif self.timeStampType == "Weekly":
                self.exchange_rates = self.cryptoInfo.get_weekly()
            elif self.timeStampType == "Monthly":
                self.exchange_rates = self.cryptoInfo.get_monthly()
            elif self.timeStampType == "this Year":
                self.exchange_rates = self.cryptoInfo.get_this_year()
            elif self.timeStampType == "Yearly":
                self.exchange_rates = self.cryptoInfo.get_yearly()

        keySet = self.exchange_rates.keys()
        highPrices = self.exchange_rates.get(keySet[0])
        lowPrices = self.exchange_rates.get(keySet[1])

        # x = [time.timestamp() for time in self.exchange_rates.index]
        # x = lowPrices.index.astype('int64')//10**9
        self.x = lowPrices.index
        self.y = lowPrices.values
        # plot the pandas DataFrame, passing in the matplotlib Canvas axes.


        self.sc = sns.lineplot(ax=self.ax, x=self.x, y=self.y,color = "orange",marker="o",markersize=3)

        self.ax.tick_params(axis='x', rotation=15)
        # print(x[10])
        # print(lowPrices.index[10])

        # self.min_x, self.max_x = x.min(), x.max()
        # self.min_y,self.max_y = y.min(), y.max()
        self.min_x, self.max_x = pd.to_datetime(self.x.min().timestamp() * 0.95, unit='s'), pd.to_datetime(
            self.x.max().timestamp() * 1.05, unit='s')
        self.min_y, self.max_y = self.y.min() * 0.95, self.y.max() * 1.05
        self.lnx = plt.plot([self.x.min(),self.x.min()], [self.y.min(), self.y.min()], color='white', linewidth=0.3)
        self.lny = plt.plot([self.x.min(),self.x.max()], [self.y.min(), self.y.min()], color='white', linewidth=0.3)
        self.lnx[0].set_linestyle('None')
        self.lny[0].set_linestyle('None')
        # get points from plot
        self.annot = self.ax.annotate("", xy=(0, 0), xytext=(40, 20), textcoords="offset points", ha='center', va='bottom'\
                                      ,bbox=dict(boxstyle='round,pad=0.2', fc='gray', alpha=0.5), \
                                      arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.5',
                                                      color='red')
                                      )
        self.annot.set_visible(False)




        # self.exchange_rates.plot(ax=self.sc.axes, y='low')

        # alternatively plot x and y prepared sets of data
        # self.sc.axes.plot(x, y)
        self.canvas.draw_idle()
        # self.sc.draw()

    def hover(self, event):
        if event.inaxes == self.ax:
            # print(event.xdata, event.ydata)
            self.lnx[0].set_data([event.xdata, event.xdata], [self.min_y, self.max_y])
            # print(self.lnx[0].get_data())
            self.lnx[0].set_linestyle('--')
            self.lny[0].set_data([self.min_x,self.max_x], [event.ydata, event.ydata])
            self.lny[0].set_linestyle('--')
            self.lnx[0].set_visible(True)
            self.lny[0].set_visible(True)

            # get the points contained in the event
            lines = self.sc.get_lines()[0]
            points = lines.contains(event)
            if points[0]:
                lines_data = lines.get_data()
                ind = points[1]["ind"][0]
                self.annot.xy = (lines_data[0][ind], lines_data[1][ind])

                self.annot.set_text(
                    "Date: {} \nPrice: {}$".format(self.x[ind], self.y[ind]))
                self.annot.set_visible(True)
            else:
                self.annot.set_visible(False)
        else:
            self.lnx[0].set_visible(False)
            self.lny[0].set_visible(False)
        self.canvas.draw_idle()
        self.canvas.flush_events()






if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PlotWindow()
    window.show()
    sys.exit(app.exec_())

