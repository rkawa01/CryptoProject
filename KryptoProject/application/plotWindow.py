import sys

from PyQt5.QtCore import pyqtSignal, QObject, QThread
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, \
    QPushButton, QLineEdit, QDoubleSpinBox, QInputDialog, QMessageBox, QDesktopWidget
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


# class MplCanvas(FigureCanvas):
#
#     def __init__(self, parent=None, width=5, height=4, dpi=100):
#         fig = Figure(figsize=(width, height), dpi=dpi)
#         self.axes = fig.add_subplot(111)
#         super(MplCanvas, self).__init__(fig)

class CustomLabel(QLabel):
    def __init__(self, fixed_text, currency, parent=None):
        super().__init__(parent)
        self.fixed_text = fixed_text
        self.currency = currency
        self.update_label()

    def update_label(self, variable_text="",number = False):
        if number:
            # round to 2 places after decimal
            self.setText(self.fixed_text + str(round(float(variable_text), 2)) + self.currency)
        else:
            self.setText(self.fixed_text + variable_text + self.currency)
        self.adjustSize()

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
    def __init__(self,request = None ,parent=None, username="User", width = 1920, height = 1080):
        super(PlotWindow, self).__init__(parent)
        # set larger size of the window
        window_width = int(width * 0.8)
        window_height = int(height * 0.8)
        self.setGeometry(
            int(QDesktopWidget().availableGeometry().center().x() - window_width / 2),
            int(QDesktopWidget().availableGeometry().center().y() - window_height / 2),
            window_width,
            window_height,
        )
        self.username = username
        self.request = request
        self.timeStampType = None
        self.cryptoInfo = Crypto("BTC", "USD", 2000, "CCCAGG")
        # Get user data
        self.wallet = 0.0
        self.bit = 0.5
        self.balance = 0.0
        if self.request and self.request.info:
            self.request.getResponse()
            self.wallet = self.request.info['wallet']
            self.bit = self.request.info['bit']
            self.balance = self.request.info['balance']

        # Create threads
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

        self.thread.start()


    def init(self):

        userLayout = QHBoxLayout()
        textLayout = QVBoxLayout()

        userName = QLabel("UserName:   " + self.username)
        self.bitcoinsOwned = CustomLabel("My bitcoins:   ", " BTC")
        self.walletState = CustomLabel("My wallet state:   ", " USD")
        self.currentValue = CustomLabel("Bitcoin buy price:   ", " USD")
        self.bitcoinsValue = CustomLabel("My Bitcoins value as of now:   ", " USD")
        self.accountBalance = CustomLabel("Account balance:   ", " USD")


        textLayout.addWidget(userName)
        textLayout.addWidget(self.bitcoinsOwned)
        textLayout.addWidget(self.walletState)
        textLayout.addWidget(self.currentValue)
        textLayout.addWidget(self.bitcoinsValue)
        textLayout.addWidget(self.accountBalance)

        buySellLayout = QVBoxLayout()
        buyLayout = QHBoxLayout()
        sellLayout = QHBoxLayout()

        self.buySpinBox = QDoubleSpinBox()
        self.buySpinBox.setDecimals(4)
        self.buySpinBox.setMaximum(self.wallet / self.cryptoInfo.get_price_now())
        self.sellSpinBox = QDoubleSpinBox()
        self.sellSpinBox.setDecimals(4)
        self.sellSpinBox.setMaximum(self.bit)

        buyButton = QPushButton("Buy")
        buyButton.clicked.connect(lambda: self.buy())
        sellButton = QPushButton("Sell")
        sellButton.clicked.connect(lambda: self.sell())


        buyLayout.addWidget(self.buySpinBox)
        sellLayout.addWidget(self.sellSpinBox)
        buyLayout.addWidget(buyButton)
        sellLayout.addWidget(sellButton)
        buySellLayout.addLayout(buyLayout)
        buySellLayout.addLayout(sellLayout)

        self.update_labels()

        # Create the seaborn FigureCanvas object, which defines a single set of axes as self.axes.
        # self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        # toolbar = NavigationToolbar(self.sc, self)
        plot_layout = QVBoxLayout()
        # plot_layout.addWidget(toolbar)
        # plot_layout.addWidget(self.sc)
        # Both alternatives version of changing the background color of the plot area
        sns.set(rc={'axes.facecolor': '#444444', 'figure.facecolor': '#444444', 'axes.grid': False, 'axes.labelcolor': 'white', 'text.color': 'white',
                    'xtick.color': 'white', 'ytick.color': 'white', 'axes.edgecolor': 'gray', 'axes.titlecolor': 'white'})
        # This with less options
        # plt.style.use("dark_background")
        self.figure = plt.figure()
        plt.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.2)
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
    def buy(self):
        cost = self.cryptoInfo.get_price_now() * self.buySpinBox.value()
        if self.wallet < cost:
            msg_box = QMessageBox()
            msg_box.setText("Not enough money.")
            msg_box.setWindowTitle("Error buying")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()
            return
        self.bit += self.buySpinBox.value()

        self.wallet -= cost
        self.balance -= cost

        if self.request and self.request.info:
            url = 'http://127.0.0.1:8000/crypto/index/'
            params = {"bit": str(self.bit), "wallet": str(self.wallet), "balance": str(self.balance)}
            self.request.postResponse(url, params)

        self.update_labels()
    def sell(self):

        self.bit -= self.sellSpinBox.value()
        profit = self.cryptoInfo.get_price_now() * self.sellSpinBox.value()
        self.wallet += profit
        self.balance += profit
        if self.request and self.request.info:
            url = 'http://127.0.0.1:8000/crypto/index/'
            params = {"bit":str(self.bit),"wallet":str(self.wallet),"balance":str(self.balance)}
            self.request.postResponse(url,params)

        self.update_labels()
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
        self.ema_short = self.exchange_rates['close'].ewm(span=20, adjust=False).mean()
        self.ema_long = self.exchange_rates['close'].ewm(span=100, adjust=False).mean()
        if (self.timeStampType):
            # if you want to retrieve some data from the request

            if self.timeStampType == "Daily":
                self.exchange_rates = self.cryptoInfo.get_daily()
                self.ema_short = self.exchange_rates['close'].ewm(span=50, adjust=False).mean()
                self.ema_long = self.exchange_rates['close'].ewm(span=200, adjust=False).mean()
            elif self.timeStampType == "Weekly":
                self.exchange_rates = self.cryptoInfo.get_weekly()
                self.ema_short = self.exchange_rates['close'].ewm(span=20, adjust=False).mean()
                self.ema_long = self.exchange_rates['close'].ewm(span=100, adjust=False).mean()
            elif self.timeStampType == "Monthly":
                self.exchange_rates = self.cryptoInfo.get_monthly()
                self.ema_short = self.exchange_rates['close'].ewm(span=20, adjust=False).mean()
                self.ema_long = self.exchange_rates['close'].ewm(span=100, adjust=False).mean()
            elif self.timeStampType == "this Year":
                self.exchange_rates = self.cryptoInfo.get_this_year()
                self.ema_short = self.exchange_rates['close'].ewm(span=20, adjust=False).mean()
                self.ema_long = self.exchange_rates['close'].ewm(span=100, adjust=False).mean()
            elif self.timeStampType == "Yearly":
                self.exchange_rates = self.cryptoInfo.get_yearly()
                self.ema_short = self.exchange_rates['close'].ewm(span=50, adjust=False).mean()
                self.ema_long = self.exchange_rates['close'].ewm(span=200, adjust=False).mean()

        close_prices = self.exchange_rates.get('close')
        # print last value of the DataFrame with date as index

        # x = [time.timestamp() for time in self.exchange_rates.index]
        # x = lowPrices.index.astype('int64')//10**9
        self.x = close_prices.index
        self.y = close_prices.values
        # plot the pandas DataFrame, passing in the matplotlib Canvas axes.
        # sns.set_style("darkgrid")

        self.sc = sns.lineplot(ax=self.ax, x=self.x, y=self.y,color = "orange",linewidth=0.7)
        sns.lineplot(ax=self.ax, x=self.x, y=self.ema_short, color="green", label = "Short",linewidth=1)
        sns.lineplot(ax=self.ax, x=self.x, y=self.ema_long, color="red", label = "Long",linewidth=1)

        # plt.fill_between(self.x, self.y, alpha=0.3)

        self.ax.legend(self.ax.get_legend_handles_labels()[0], self.ax.get_legend_handles_labels()[1],title = 'Moving average')
        self.ax.set_ylabel('Price in dollars')
        self.ax.set_xlabel('Date')

        self.ax.tick_params(axis='x', rotation=15)

        # self.min_x, self.max_x = x.min(), x.max()
        # self.min_y,self.max_y = y.min(), y.max()
        self.min_x, self.max_x = pd.to_datetime(self.x.min().timestamp() * 0.95, unit='s'), pd.to_datetime(
            self.x.max().timestamp() * 1.05, unit='s')
        self.min_y, self.max_y = self.y.min() * 0.95, self.y.max() * 1.05
        self.lnx = plt.plot([self.x.min(),self.x.min()], [self.y.min(), self.y.min()], color='white', linewidth=0.3)
        self.lny = plt.plot([self.x.min(),self.x.max()], [self.y.min(), self.y.min()], color='white', linewidth=0.3)
        self.lnx[0].set_linestyle('None')
        self.lny[0].set_linestyle('None')
        # set annotations
        self.annot = self.ax.annotate("", xy=(0, 0), xytext=(40, 20), textcoords="offset points", ha='center', va='bottom',
                                      bbox=dict(boxstyle='round,pad=0.2', fc='gray', alpha=0.5),
                                      arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.5',
                                                      color='red'))
        self.annot.set_visible(False)


        # mplcursors.cursor(self.sc, hover=True)
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
            self.lny[0].set_data([self.min_x, self.max_x], [event.ydata, event.ydata])
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

    def update_runtime(self):
        current_price = self.cryptoInfo.get_price_now()
        self.currentValue.update_label(current_price,number = True)
        self.bitcoinsValue.update_label(current_price * self.bit, number = True)
        # self.bitcoinsValue.setText(
        #     "My Bitcoins value as of now:   " + str(self.cryptoInfo.get_price_now() * self.bit) + " USD")
        # self.currentValue.setText("Bitcoin buy price:   " + str(self.cryptoInfo.get_price_now()) + " USD")
        self.get_plot()
    def update_request(self, message):

        self.timeStampType = message
        self.get_plot()

    def update_labels(self):
        current_price = self.cryptoInfo.get_price_now()

        self.sellSpinBox.setMaximum(self.bit)
        self.buySpinBox.setMaximum(self.wallet / current_price)

        self.walletState.update_label(self.wallet, number = True)
        self.bitcoinsOwned.update_label(self.bit, number = True)
        self.currentValue.update_label(current_price,number = True)
        self.bitcoinsValue.update_label(self.bit*current_price, number = True)
        self.accountBalance.update_label(self.balance, number = True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    width = app.desktop().screenGeometry().width()
    height = app.desktop().screenGeometry().height()
    window = PlotWindow(width = width, height = height)
    window.show()
    sys.exit(app.exec_())

