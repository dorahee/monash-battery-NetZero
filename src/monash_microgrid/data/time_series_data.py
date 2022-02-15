import pandas as pd
from src.monash_microgrid.data import dataIO
from src.monash_microgrid.common.param import *


class TimeSeriesData(dataIO.DataIO):

    def __init__(self):
        super().__init__()

        self.minutes_interval = 0
        self.num_intervals_hour = 0
        self.num_intervals_horizon = 0
        self.start_date_time = ""
        self.end_date_time = ""
        self.observation_time = ""

        self.sod_interval = 0
        self.eod_interval = 0
        self.horizon_intervals = []
        self.eod_index = 0

        self.unit = ""
        self.freq = ""

    def dict_to_dataframe(self):
        time_series_dict = self.data_dict
        # add the date times
        self.data_df = pd.DataFrame(
            {d_datetime: pd.to_datetime(time_series_dict[d_datetime][d_value])}
        )
        self.minutes_interval = int(time_series_dict[d_datetime][d_freq])
        self.num_intervals_hour = int(60 / self.minutes_interval)

        self.start_date_time = self.data_df[d_datetime][0]
        self.end_date_time = self.data_df[d_datetime][self.data_df[d_datetime].size - 1]

        # convert consumptions to demands if demands are not given
        if d_consumption in time_series_dict and d_demand not in time_series_dict:
            self.unit = time_series_dict[d_consumption][d_unit]
            self.data_df[d_demand] = [d * self.num_intervals_hour for d in time_series_dict[d_consumption][d_value]]
            self.num_intervals_horizon = self.data_df[d_demand].size

        # or add demands
        elif d_demand in time_series_dict:
            self.unit = time_series_dict[d_demand][d_unit]
            self.data_df[d_demand] = time_series_dict[d_demand][d_value]
            self.num_intervals_horizon = self.data_df[d_demand].size

        # or add prices
        elif d_price in time_series_dict:
            self.unit = time_series_dict[d_price][d_unit]
            self.data_df[d_price] = time_series_dict[d_price][d_value]
            self.num_intervals_horizon = self.data_df[d_price].size

        # or add other values
        else:
            self.data_df[d_data] = time_series_dict[d_data][d_value]
            self.num_intervals_horizon = self.data_df[d_data].size

        # calculate the time intervals in the scheduling horizon
        self.sod_interval = int((self.start_date_time.hour * 60 + self.start_date_time.minute) / self.minutes_interval)
        self.eod_interval = self.sod_interval + self.num_intervals_horizon
        self.horizon_intervals = [x for x in range(self.sod_interval, self.eod_interval)]
        self.eod_index = self.horizon_intervals.index(self.eod_interval - 1)

        # set the index of the demands data frame
        # todo: test removing some values
        self.data_df = self.data_df.set_index(d_datetime)

        # for testing
        # True
