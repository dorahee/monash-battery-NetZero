from src.monash_microgrid.common.param import *
import json, pandas as pd


class Schedule:

    def __init__(self):
        self.schedules = dict()
        self.schedules_df = pd.DataFrame()

        self.minute_interval = 0
        self.num_intervals_hour = 0
        self.num_intervals_horizon = 0

        self.status = status_none

    def new(self, batteries, forecasts, service):
        self.status = service.status
        self.minute_interval = forecasts.minutes_interval
        self.num_intervals_hour = int(60 / self.minute_interval)
        self.num_intervals_horizon = forecasts.num_intervals_horizon

        self.schedules = dict()
        for battery_name, ch, disch, soc in \
                zip(batteries.data_dict.keys(), service.charges, service.discharges, service.socs):
            self.schedules[battery_name] = dict()
            self.schedules[battery_name][d_datetime] = \
                [x.strftime('%Y-%m-%d %H:%M') for x in forecasts.data_df.index]
            self.schedules[battery_name][b_charges] = list(ch)
            self.schedules[battery_name][b_discharges] = list(disch)
            self.schedules[battery_name][b_soc] = list(soc)
        self.schedules[b_agg_demands] = list(service.agg_battery_demands)
        self.to_dataframe()

    def to_json(self):
        json_str = json.dumps(self.schedules)
        return json_str

    def to_json_file(self, file_name):
        json_str = self.to_json()
        with open(file_name, "w") as f:
            json.dump(json_str, f, indent=2)
        return json_str

    def read(self, json_str, json_file):
        try:
            if json_str is not None and json_str != "":
                self.from_json(json_str)
            else:
                self.from_json_file(json_file)
            self.to_dataframe()
            return True
        except:
            return False

    def from_json(self, json_str):
        self.schedules = json.loads(json_str)

    def from_json_file(self, file_name):
        json_str = json.load(open(file_name))
        self.from_json(json_str)


