# this script generates the forecast demands and the actual demands for experiments
import pandas as pd
from src.monash_microgrid.data import dataIO
from src.monash_microgrid.common.param import *


class DemandDataSet(dataIO.DataIO):

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

        # the name of the demand column
        self.col_demand = ""
        self.col_consumption = ""
        self.col_price = ""

    def read_from_csv(self, file_name):
        # read the data from a csv file into a pandas data frame
        df = pd.read_csv(f"{file_name}")

        # read the name of the date time column and the name of the demand column
        col_datetime = df.columns[0]
        col_consumption = df.columns[1]
        self.col_timestamp = col_datetime
        self.col_consumption = col_consumption

        # convert the datetime strings into Timestamp objects
        df[col_datetime] = pd.to_datetime(df[col_datetime])

        # calculate the minutes between every two timestamps
        self.minutes_interval = abs(df[col_datetime][1].minute - df[col_datetime][0].minute)

        # change the name of the date time column to a predefined value
        df.rename(columns={col_datetime: d_datetime}, inplace=True)

        # set the index of the data frame
        df = df.set_index(d_datetime)
        self.dataset_df = df

        # calculate the number of intervals in each hour/day
        self.num_intervals_hour = int(60 / self.minutes_interval)
        self.num_intervals_day = int(1440 / self.minutes_interval)
