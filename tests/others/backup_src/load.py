import pandas as pd
from src.monash_battery.param import *


class Forecast:

    def __init__(self):
        self.minutes_interval = 0
        self.num_intervals_hour = 0
        self.num_intervals_day = 0
        self.dataset = pd.DataFrame()
        self.col_datetime = ""
        self.forecast_demands = pd.DataFrame()

    def new_dataset(self, file_name):
        df = pd.read_csv(f"{file_name}")
        col_datetime = df.columns[0]
        df[col_datetime] = pd.to_datetime(df[col_datetime])
        freq = df[col_datetime][1].minute - df[col_datetime][0].minute

        self.dataset = df
        self.col_datetime = col_datetime
        self.minutes_interval = freq
        self.num_intervals_hour = int(60 / freq)
        self.num_intervals_day = int(1440 / self.minutes_interval)

        print("Forecast load dataset is added. ")

    def read_forecast_loads(self, start_time):
        loads_df = self.dataset
        mask = (loads_df[self.col_datetime] == start_time)
        df = loads_df.loc[mask]
        self.forecast_demands = pd.DataFrame()
        try:
            loads2 = list(df.iloc[0, 1:])
            self.forecast_demands[d_datetime] = pd.date_range(start=start_time, periods=len(loads2),
                                                              freq=f"{self.minutes_interval}min")
            self.forecast_demands[d_demand] = [l * self.num_intervals_hour for l in loads2]
            return True
        except IndexError:
            return False


class Historical:

    def __init__(self):
        self.minutes_interval = 0
        self.num_intervals_hour = 0
        self.num_intervals_day = 0
        self.dataset = ""
        self.col_datetime = ""
        self.col_loads = ""
        self.forecast_demands = pd.DataFrame()
        self.historical_demands = pd.DataFrame()

    def new_dataset(self, file_name):
        df = pd.read_csv(f"{file_name}")
        col_datetime = df.columns[0]
        col_loads = df.columns[1]
        df[col_datetime] = pd.to_datetime(df[col_datetime])
        freq = df[col_datetime][1].minute - df[col_datetime][0].minute
        df.set_index(col_datetime)

        self.dataset = df
        self.col_datetime = col_datetime
        self.col_loads = col_loads
        self.minutes_interval = freq
        self.num_intervals_hour = int(60 / freq)
        self.num_intervals_day = int(1440 / self.minutes_interval)

        print("Actual load dataset is added. ")

    def read_historical_loads(self, start_time, reschedule_freq):
        loads_df = self.dataset
        col_datetime = self.col_datetime
        col_loads = self.col_loads
        end_time = start_time + reschedule_freq
        mask = (loads_df[col_datetime] >= start_time) & (loads_df[col_datetime] < end_time)
        df = loads_df.loc[mask]
        loads = list(df[col_loads])
        self.historical_demands = pd.DataFrame()
        self.historical_demands[d_datetime] = \
            pd.date_range(start=start_time, periods=len(loads), freq=f"{self.minutes_interval}min")
        self.historical_demands[d_demand] = [l * self.num_intervals_hour for l in loads]

        end_time1 = start_time + pd.Timedelta(minutes=self.minutes_interval * self.num_intervals_day)
        mask2 = (loads_df[col_datetime] >= start_time) & (loads_df[col_datetime] < end_time1)
        df2 = loads_df.loc[mask2]
        loads2 = list(df2[col_loads])
        self.forecast_demands = pd.DataFrame()
        self.forecast_demands[d_datetime] = pd.date_range(start=start_time, periods=len(loads2),
                                                          freq=f"{self.minutes_interval}min")
        self.forecast_demands[d_demand] = [l * self.num_intervals_hour for l in loads2]
