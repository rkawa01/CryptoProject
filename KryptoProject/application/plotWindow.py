import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QBrush, QColor, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QSizePolicy, QWidget, QHBoxLayout, QVBoxLayout, QLabel
import cryptocompare
import pandas as pd
from datetime import datetime,date,timedelta
import cplot
import pyqtgraph as pg

class PlotWindow(QMainWindow):
    def __init__(self,request = None ,parent=None):
        super(PlotWindow, self).__init__(parent)
        self.request = request
        # Create a central widget to hold the layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.graphWidget = pg.PlotWidget()
        # self.setCentralWidget(self.graphWidget)

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
        # self.layout.addLayout(self.plot_layout)
        self.layout.addWidget(self.graphWidget)
        self.layout.addStretch()
        self.get_plot()

    def resizeEvent(self, event):
        # Resize the plot placeholder label to be centered in the upper half of the window
        rect = self.geometry()
        plot_height = rect.height() // 2
        plot_width = self.plot_layout.geometry().width()
        self.plot_label.setFixedHeight(plot_height)
        self.plot_layout.setContentsMargins((rect.width() - plot_width) // 2, plot_height // 2, 0, 0)

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
        # if(self.request):
            #if you want to retrieve some data from the request
            # self.request.getresponse()
            # print(self.request.info)
        self.ticker_symbol = 'BTC'
        self.currency = 'USD'
        self.limit_value = 2000
        self.exchange_name = 'CCCAGG'


        # print(self.get_this_year())
        # print(self.get_daily())
        records = self.get_weekly()
        # records.plot()
        # print(records)
        # print(records.index.values)
        keySet = records.keys()

        print(keySet)

        highPrices = []
        lowPrices = []
        openDate = []


        for key in keySet:
            print(key)
        lowPrices = records.get(keySet[1])
        times = records.get(keySet[2])

        print(lowPrices.index)
        # print(times)
        # for lowPrice in records.get(keySet[1]):
        #     print(lowPrice)
        #
        self.graphWidget.plot(lowPrices.index, lowPrices, pen = None, symbol = 'o')
        # lowPrices.plot()




if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PlotWindow()
    window.show()
    sys.exit(app.exec_())

# To execute get_plot or something every 5 minutes
# import time
#
# while (True):
#     print('hello geek!')
#     time.sleep(300)