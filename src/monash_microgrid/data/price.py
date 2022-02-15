# this script generates the forecast demands and the actual demands for experiments
import pandas as pd
from src.monash_microgrid.data import dataIO, price_dataset
from src.monash_microgrid.common.param import *


class PriceForecasts(price_dataset.PriceDataSet):

    def __init__(self):
        super().__init__()

    def read_prices(self, price_type, observation_time, horizon_end_time,
                    horizon_start_time_limit, horizon_end_time_limit):

        self.observation_time = observation_time
        self.start_time = observation_time + pd.Timedelta(minutes=self.minutes_interval)
        self.end_time = horizon_end_time

        self.data_dict = dict()
        self.data_dict[d_datetime] = dict()
        self.data_dict[d_datetime][d_value] \
            = pd.date_range(start=self.start_time, end=horizon_end_time, freq=f"{self.minutes_interval}min")
        self.data_dict[d_datetime][d_freq] = self.minutes_interval

        self.data_dict[d_price] = dict()
        df = self.dataset_df[self.dataset_df.index == pd.to_datetime(observation_time)].copy()
        df[self.col_price] = df[self.col_price].mul(1000.0)
        if df.size > 0:
            new_prices = list(df[self.col_price][:self.data_dict[d_datetime][d_value].size])
            self.data_dict[d_price][d_value] = new_prices
            self.data_dict[d_price][d_unit] = d_dollar_kwh
            self.data_dict[d_price][d_type] = price_type

            return True
        else:
            return False

        # for testing
        # True


class HistoricPrices(price_dataset.PriceDataSet):

    def __init__(self):
        super().__init__()

    def read_prices(self, price_type, observation_time, horizon_end_time,
                    horizon_start_time_limit, horizon_end_time_limit):


        col_datetime = self.col_timestamp
        if col_datetime in self.dataset_df:
            self.dataset_df = self.dataset_df.set_index(col_datetime)

        col_price = self.col_price

        self.observation_time = observation_time
        self.start_time = observation_time + pd.Timedelta(minutes=self.minutes_interval)
        try:
            df = self.dataset_df[self.start_time: horizon_end_time]. \
                between_time(horizon_start_time_limit, horizon_end_time_limit, include_start=True, include_end=False)
        except:
            return False
        # df[d_demand] = [l * self.num_intervals_hour for l in list(df[col_loads])]

        if df.size > 0:
            self.data_dict = dict()
            self.data_dict[d_datetime] = dict()
            self.data_dict[d_datetime][d_value] = pd.to_datetime(df.index.values)
            self.data_dict[d_datetime][d_freq] = self.minutes_interval

            self.data_dict[d_price] = dict()
            self.data_dict[d_price][d_value] = list(df[d_price].values)
            self.data_dict[d_price][d_unit] = d_dollar_kwh
            self.data_dict[d_price][d_type] = price_type

            return True
        else:
            return False

        # for testing
        # True
