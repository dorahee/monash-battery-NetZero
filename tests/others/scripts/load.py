import pandas as pd


class Loads:

    def __init__(self):
        self.num_intervals_day = 0
        self.minutes_interval = 0
        self.num_intervals_hour = 0

        self.historical_loads_df = pd.DataFrame()
        self.current_historical_demands = []
        self.current_historical_datetime_range = []
        self.historical_column_load = ""
        self.historical_column_datetime = ""
        self.historical_minutes_interval = 0

        self.actual_loads_df = pd.DataFrame()
        self.current_actual_demands = []
        self.current_actual_datetime_range = []
        self.actual_column_load = ""
        self.actual_column_datetime = ""
        self.actual_minutes_interval = 0

        self.forecast_loads_df = pd.DataFrame()
        self.current_forecast_demands = []
        self.current_forecast_datetime_range = []
        self.forecast_column_load = ""
        self.forecast_column_datetime = ""
        self.forecast_minutes_interval = 0

    def new_historical_loads(self, file_name, i_col_loads, i_col_datetime=0):
        df = pd.read_csv(f"{file_name}")
        col_load = df.columns[i_col_loads]
        col_datetime = df.columns[i_col_datetime]
        df[col_datetime] = pd.to_datetime(df[col_datetime])
        freq = df[col_datetime][1].minute - df[col_datetime][0].minute

        self.historical_loads_df = df
        self.historical_column_load = col_load
        self.historical_column_datetime = col_datetime
        self.historical_minutes_interval = int(freq)

        self.minutes_interval = max(self.minutes_interval, self.historical_minutes_interval)
        self.num_intervals_day = int(1440 / self.minutes_interval)
        self.num_intervals_hour = int(60 / self.minutes_interval)
        print("Historical data is added. ")

    def new_forecast_loads(self, file_name, i_col_loads, forecast_type, header, i_col_datetime=0):
        df = pd.read_csv(f"{file_name}", header=header)
        col_datetime = df.columns[i_col_datetime]
        col_loads = df.columns[i_col_loads]
        df[col_datetime] = pd.to_datetime(df[col_datetime])
        freq = df[col_datetime][1].minute - df[col_datetime][0].minute

        self.forecast_loads_df = df
        self.forecast_column_load = col_loads
        self.forecast_column_datetime = col_datetime
        self.forecast_minutes_interval = int(freq)

        self.minutes_interval = max(self.minutes_interval, self.forecast_minutes_interval)
        self.num_intervals_day = int(1440 / self.minutes_interval)
        self.num_intervals_hour = int(60 / self.minutes_interval)

        # if forecast_type == l_frits_forecast:
        #     df[col_datetime] = df[col_datetime] + pd.Timedelta(minutes=self.minutes_interval)

        print(f"Forecast data (type {forecast_type}) is added. ")

    def read_historical_loads(self, start_time, end_time, unit, loads_type):
        loads_df = self.historical_loads_df
        col_datetime = self.historical_column_datetime
        col_loads = self.historical_column_load

        mask = (loads_df[col_datetime] >= start_time) & (loads_df[col_datetime] < end_time)
        df = loads_df.loc[mask]
        if "k" not in unit:
            loads2 = [l / 1000 for l in list(df[col_loads])]
        else:
            loads2 = list(df[col_loads])
        demands = [l * self.num_intervals_hour for l in loads2]

        self.current_historical_demands = demands
        self.current_historical_datetime_range = pd.date_range(start=start_time,
                                                               end=end_time,
                                                               freq=f"{int(self.minutes_interval)}min")

        return True

    def read_forecast_loads(self, start_time, end_time, loads_type):

        loads_df = self.forecast_loads_df
        col_datetime = self.forecast_column_datetime

        if loads_type == l_frits_forecast:
            mask = (loads_df[col_datetime] == start_time)
            df = loads_df.loc[mask]
            if df.empty:
                return False
            else:
                loads2 = list(df.iloc[0, 1:])

        else:
            mask = (loads_df[col_datetime] >= start_time) & (loads_df[col_datetime] < end_time)
            df = loads_df.loc[mask]
            loads2 = [l for l in list(df[self.forecast_column_load])]

        demands = [l * self.num_intervals_hour for l in loads2]
        self.current_forecast_demands = demands
        self.current_forecast_datetime_range = pd.date_range(start=start_time,
                                                             periods=self.num_intervals_day,
                                                             freq=f"{int(self.minutes_interval)}min")

        if len(demands) != self.num_intervals_day:
            return False
        else:
            return True
