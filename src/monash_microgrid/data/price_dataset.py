# this script generates the forecast demands and the actual demands for experiments
import pandas as pd
from src.monash_microgrid.data import dataIO
from src.monash_microgrid.common.param import *
import pyreadr, numpy as np


class PriceDataSet(dataIO.DataIO):

    def __init__(self):
        super().__init__()

        # the number of minutes in a time interval
        self.minutes_interval = 0

        # the number of time intervals in an hour
        self.num_intervals_hour = 0

        # the number of time intervals in a day
        self.num_intervals_day = 0
        self.start_time = ""
        self.end_time = ""
        self.observation_time = ""

        # df means pandas data frame
        self.dataset_df = pd.DataFrame()

        # the name of the timestamp column
        self.col_timestamp = ""
        self.col_timestamp_now = ""
        self.col_timestamp_future = ""

        # the name of the price column
        self.col_price = ""

    def read_from_csv(self, file_name):
        # read the data from a csv file into a pandas data frame
        df = pd.read_csv(f"{file_name}")

        # read the name of the date time column and the name of the demand column
        self.col_timestamp_now = df.columns[0]
        self.col_timestamp_future = df.columns[1]
        self.col_price = df.columns[2]

        # convert the datetime strings into Timestamp objects
        def convert(col_name):
            df[col_name] = pd.to_datetime(df[col_name])
        convert(self.col_timestamp_now)
        convert(self.col_timestamp_future)

        # calculate the minutes between every two timestamps
        col_datetime = self.col_timestamp_future
        self.minutes_interval = abs(df[col_datetime][1].minute - df[col_datetime][0].minute)

        # change the name of the date time column to a predefined value
        col_datetime = self.col_timestamp_now
        df.rename(columns={col_datetime: d_datetime}, inplace=True)

        # set the index of the data frame
        df = df.set_index(d_datetime)
        df.index = df.index.round(freq='30T')
        self.dataset_df = df

        # calculate the number of intervals in each hour/day
        self.num_intervals_hour = int(60 / self.minutes_interval)
        self.num_intervals_day = int(1440 / self.minutes_interval)

    def read_from_csv2(self, file_name):
        # read the data from a csv file into a pandas data frame
        df = pd.read_csv(f"{file_name}")

        # read the name of the date time column and the name of the demand column
        self.col_timestamp_now = df.columns[0]
        # self.col_timestamp_future = df.columns[1]
        self.col_price = df.columns[2]

        # convert the datetime strings into Timestamp objects
        def convert(col_name):
            df[col_name] = pd.to_datetime(df[col_name])
        convert(self.col_timestamp_now)
        # convert(self.col_timestamp_future)

        # calculate the minutes between every two timestamps
        col_datetime = self.col_timestamp_now
        self.minutes_interval = abs(df[col_datetime][1].minute - df[col_datetime][0].minute)

        # change the name of the date time column to a predefined value
        df.rename(columns={col_datetime: d_datetime}, inplace=True)

        # set the index of the data frame
        df = df.set_index(d_datetime)
        df.index = df.index.round(freq='30T')
        df = df.loc["2019-12-01 00:00":"2021-01-01 00:00"]
        self.dataset_df = df

        # calculate the number of intervals in each hour/day
        self.num_intervals_hour = int(60 / self.minutes_interval)
        self.num_intervals_day = int(1440 / self.minutes_interval)

    def read_from_rds(self, data_folder, file_name):
        result = pyreadr.read_r(file_name)
        df1 = result[None]
        all_region_ids = set(df1.REGIONID)
        vic_regions = [x for x in all_region_ids if "VIC" in x]
        df2 = df1[(df1.REGIONID.isin(vic_regions))]
        df2.to_csv(f"{data_folder}dispatch_prices.csv", index=False)
        print()



