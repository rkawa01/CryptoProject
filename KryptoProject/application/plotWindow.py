import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QBrush, QColor, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QSizePolicy, QWidget, QHBoxLayout, QVBoxLayout, QLabel, \
    QPushButton
import cryptocompare
import pandas as pd
from datetime import datetime,date,timedelta
import pyqtgraph as pg
from getInfo import JsonInfo


class DateTimeAxis(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        # Convert the tick values to datetime format
        return [pd.to_datetime(value, unit='s').strftime('%Y-%m-%d %H:%M:%S') for value in values]

class PlotWindow(QMainWindow):
    def __init__(self,request = None ,parent=None):
        super(PlotWindow, self).__init__(parent)
        self.request = request
        self.timeStampType = None
        # Get user data
        self.wallet = 0
        self.bit = 0
        if self.request and self.request.info:
            self.request.getresponse()
            self.wallet = self.request.info['wallet']
            self.bit = self.request.info['bit']

        # Create a central widget to hold the layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create a vertical layout to hold the plot placeholder and other widgets
        self.layout = QVBoxLayout(self.central_widget)

        self.plot_widget = pg.PlotWidget(axisItems={'bottom': DateTimeAxis(orientation='bottom')})
        # self.graphWidget = pg.PlotWidget()

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
        self.layout.addWidget(self.plot_widget)
        self.layout.addLayout(self.buttonLayout)
        self.layout.addStretch()

        self.get_plot()

    def resizeEvent(self, event):
        # Resize the plot placeholder label to be centered in the upper half of the window
        rect = self.geometry()
        plot_height = rect.height() // 2
        plot_width = self.layout.geometry().width()

        # Call the base class resizeEvent to handle any other resizing needed
        super(PlotWindow, self).resizeEvent(event)
    def get_daily(self):
        raw_price_data = \
            cryptocompare.get_historical_price_minute(
                self.ticker_symbol,
                self.currency,
                limit=self.limit_value,
                exchange=self.exchange_name

            )
        price_data = pd.DataFrame.from_dict(raw_price_data)
        price_data.set_index("time", inplace=True)
        price_data.index = pd.to_datetime(price_data.index, unit='s')
        price_data['datetimes'] = price_data.index
        price_data['datetimes'] = price_data['datetimes'].dt.strftime('%Y-%m-%d')
        price_data = price_data[price_data['datetimes'] == str(date.today())]
        return price_data
    def get_monthly(self):
        raw_price_data = \
            cryptocompare.get_historical_price_hour(
                self.ticker_symbol,
                self.currency,
                limit=self.limit_value,
                exchange=self.exchange_name

            )
        price_data = pd.DataFrame.from_dict(raw_price_data)
        price_data.set_index("time", inplace=True)
        price_data.index = pd.to_datetime(price_data.index, unit='s')
        price_data['datetimes'] = price_data.index
        days_before = (date.today() - timedelta(days=31)).isoformat()
        price_data['datetimes'] = price_data['datetimes'].dt.strftime('%Y-%m-%d')
        price_data = price_data[price_data['datetimes'] >= days_before]
        return price_data
    def get_yearly(self):
        raw_price_data = \
            cryptocompare.get_historical_price_day(
                self.ticker_symbol,
                self.currency,
                limit=self.limit_value,
                exchange=self.exchange_name

            )
        price_data = pd.DataFrame.from_dict(raw_price_data)
        price_data.set_index("time", inplace=True)
        price_data.index = pd.to_datetime(price_data.index, unit='s')
        price_data['datetimes'] = price_data.index
        days_before = (date.today() - timedelta(days=365)).isoformat()
        price_data['datetimes'] = price_data['datetimes'].dt.strftime('%Y-%m-%d')
        price_data = price_data[price_data['datetimes'] >= days_before]
        return price_data
    def get_this_year(self):
        raw_price_data = \
            cryptocompare.get_historical_price_day(
                self.ticker_symbol,
                self.currency,
                limit=self.limit_value,
                exchange=self.exchange_name

            )
        price_data = pd.DataFrame.from_dict(raw_price_data)
        price_data.set_index("time", inplace=True)
        price_data.index = pd.to_datetime(price_data.index, unit='s')
        price_data['datetimes'] = price_data.index
        year = date.today().strftime('%Y')
        price_data['datetimes'] = price_data['datetimes'].dt.strftime('%Y')
        price_data = price_data[price_data['datetimes'] >= year]
        return price_data
    def get_weekly(self):
        raw_price_data = \
            cryptocompare.get_historical_price_hour(
                self.ticker_symbol,
                self.currency,
                limit=self.limit_value,
                exchange=self.exchange_name

            )
        price_data = pd.DataFrame.from_dict(raw_price_data)
        price_data.set_index("time", inplace=True)
        price_data.index = pd.to_datetime(price_data.index, unit='s')
        price_data['datetimes'] = price_data.index
        days_before = (date.today() - timedelta(days=7)).isoformat()
        price_data['datetimes'] = price_data['datetimes'].dt.strftime('%Y-%m-%d')
        price_data = price_data[price_data['datetimes'] >= days_before]
        return price_data
    def get_plot(self):
        self.plot_widget.clear()

        self.ticker_symbol = 'BTC'
        self.currency = 'USD'
        self.limit_value = 2000
        self.exchange_name = 'CCCAGG'
        # self.request.getresponse()
        # print(self.request.info)
        print(self.wallet)
        print(self.bit)
        exchange_rates = self.get_weekly()
        if (self.timeStampType):
            # if you want to retrieve some data from the request

            if self.timeStampType == "Daily":
                exchange_rates = self.get_daily()
            elif self.timeStampType == "Weekly":
                exchange_rates = self.get_weekly()
            elif self.timeStampType == "Monthly":
                exchange_rates = self.get_monthly()
            elif self.timeStampType == "this Year":
                exchange_rates = self.get_this_year()
            elif self.timeStampType == "Yearly":
                exchange_rates = self.get_yearly()


        keySet = exchange_rates.keys()
        highPrices = exchange_rates.get(keySet[0])
        lowPrices = exchange_rates.get(keySet[1])
        # time_labels =
        x = [time.timestamp() for time in exchange_rates.index]
        # x = lowPrices.index.astype('int64')//10**9
        y = lowPrices.values
        self.plot_widget.plot(x, y, pen='b')

        # Refresh the plot widget
        self.plot_widget.update()

    def update_request(self, message):

        self.timeStampType = message
        self.get_plot()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PlotWindow()
    window.show()
    sys.exit(app.exec_())

