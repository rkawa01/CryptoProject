import cryptocompare
import pandas as pd
from tzlocal import get_localzone
from datetime import date, timedelta


class Crypto:
    def __init__(self, ticker_symbol, currency, limit_value, exchange_name):
        self.ticker_symbol = ticker_symbol
        self.currency = currency
        self.limit_value = limit_value
        self.exchange_name = exchange_name
        self.local_tz = get_localzone()

    def get_historical_minute(self):
        raw_price_data = \
            cryptocompare.get_historical_price_minute(
                self.ticker_symbol,
                self.currency,
                limit=self.limit_value,
                exchange=self.exchange_name
            )
        price_data = pd.DataFrame(raw_price_data)
        price_data.set_index("time", inplace=True)
        price_data.index = pd.to_datetime(price_data.index, unit='s').tz_localize('UTC').tz_convert(self.local_tz)
        price_data['datetimes'] = price_data.index
        return price_data

    def get_historical_hour(self):
        raw_price_data = \
            cryptocompare.get_historical_price_hour(
                self.ticker_symbol,
                self.currency,
                limit=self.limit_value,
                exchange=self.exchange_name
            )
        price_data = pd.DataFrame(raw_price_data)
        price_data.set_index("time", inplace=True)
        price_data.index = pd.to_datetime(price_data.index, unit='s').tz_localize('UTC').tz_convert(self.local_tz)
        price_data['datetimes'] = price_data.index
        return price_data

    def get_historical_day(self):
        raw_price_data = \
            cryptocompare.get_historical_price_day(
                self.ticker_symbol,
                self.currency,
                limit=self.limit_value,
                exchange=self.exchange_name
            )
        price_data = pd.DataFrame(raw_price_data)
        price_data.set_index("time", inplace=True)
        price_data.index = pd.to_datetime(price_data.index, unit='s').tz_localize('UTC').tz_convert(self.local_tz)
        price_data['datetimes'] = price_data.index
        return price_data

    def get_price_now(self):
        raw_price = cryptocompare.get_price(self.ticker_symbol, self.currency, full=True)
        return raw_price['RAW'][self.ticker_symbol][self.currency]['PRICE']

    def get_daily(self):
        price_data = self.get_historical_minute()
        price_data['datetimes'] = price_data['datetimes'].dt.strftime('%Y-%m-%d')
        price_data = price_data[price_data['datetimes'] == str(date.today())]
        return price_data

    def get_weekly(self):
        price_data = self.get_historical_hour()
        days_before = (date.today() - timedelta(days=7)).isoformat()
        price_data['datetimes'] = price_data['datetimes'].dt.strftime('%Y-%m-%d')
        price_data = price_data[price_data['datetimes'] >= days_before]
        return price_data

    def get_monthly(self):
        price_data = self.get_historical_hour()
        days_before = (date.today() - timedelta(days=31)).isoformat()
        price_data['datetimes'] = price_data['datetimes'].dt.strftime('%Y-%m-%d')
        price_data = price_data[price_data['datetimes'] >= days_before]
        return price_data

    def get_yearly(self):
        price_data = self.get_historical_day()
        days_before = (date.today() - timedelta(days=365)).isoformat()
        price_data['datetimes'] = price_data['datetimes'].dt.strftime('%Y-%m-%d')
        price_data = price_data[price_data['datetimes'] >= days_before]
        return price_data

    def get_this_year(self):
        price_data = self.get_historical_day()
        year = date.today().strftime('%Y')
        price_data['datetimes'] = price_data['datetimes'].dt.strftime('%Y')
        price_data = price_data[price_data['datetimes'] >= year]
        return price_data


if __name__ == '__main__':
    crypto = Crypto('BTC', 'USD', 2000, 'CCCAGG')
    print(crypto.get_daily())
