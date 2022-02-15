import pandas as pd, json
from src.monash_microgrid.common.param import *


class Load:

    def __init__(self):
        self.minutes_interval = 0
        self.num_intervals_hour = 0
        self.num_intervals_day = 0
        self.num_intervals_horizon = 0

        self.forecast_demands = pd.DataFrame()
        self.historical_demands = pd.DataFrame()

        self.current_time = ""
        self.current_interval = 0
        self.previous_time = ""
        self.freq = ""

    def from_json(self, json_str):
        loads_dict = json.loads(json_str)
        self.forecast_demands = pd.DataFrame(data=loads_dict[d_forecast_original])
        self.forecast_demands[d_datetime] = pd.to_datetime(self.forecast_demands[d_datetime])
        self.current_time = self.forecast_demands[d_datetime][0]
        forecast_loads = self.forecast_demands[d_consumption]

        try:
            self.minutes_interval \
                = int((self.forecast_demands[d_datetime][1] -
                       self.forecast_demands[d_datetime][0]).total_seconds() / 60)
        except KeyError as err:
            print(err)

        try:
            self.num_intervals_day = int(1440 / self.minutes_interval)
        except ZeroDivisionError as err:
            print(err)

        self.current_interval = int((self.current_time.hour * 60 + self.current_time.minute) / self.minutes_interval)
        self.num_intervals_horizon = self.forecast_demands[d_consumption].size
        self.num_intervals_hour = int(60 / self.minutes_interval)
        self.forecast_demands[d_demand] = [l * self.num_intervals_hour for l in forecast_loads]

        self.historical_demands = pd.DataFrame(data=loads_dict[d_actual_original])
        self.historical_demands[d_datetime] = pd.to_datetime(self.historical_demands[d_datetime])
        self.previous_time = self.historical_demands[d_datetime][0]
        historical_loads = self.historical_demands[d_consumption]
        self.historical_demands[d_demand] = [l * self.num_intervals_hour for l in historical_loads]

    def from_json_file(self, file_name):
        json_str = json.load(open(file_name))
        self.from_json(json_str)
