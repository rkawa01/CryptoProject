import cryptocompare
import pandas as pd
from datetime import datetime, date, timedelta
from cachetools import TTLCache

cache = TTLCache(maxsize=100, ttl=0)
cryptocompare._cache = cache



class Crypto:
    def __init__(self, ticker_symbol, currency, limit_value, exchange_name):
        self.ticker_symbol = ticker_symbol
        self.currency = currency
        self.limit_value = limit_value
        self.exchange_name = exchange_name

    def get_price_now(self):
        raw_price = cryptocompare.get_price(self.ticker_symbol, self.currency, full=True)
        return raw_price['RAW'][self.ticker_symbol][self.currency]['PRICE']

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

if __name__ == '__main__':
    crypto = Crypto('BTC', 'USD', 2000, 'CCCAGG')
    print(crypto.get_price_now())
    # crypto.get_daily()