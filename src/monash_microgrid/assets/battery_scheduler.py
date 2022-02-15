import pandas as pd, pytz
from src.monash_microgrid.data import dataIO
from src.monash_microgrid.peak_demand_management.pdm_model import *


class BatteryScheduler(dataIO.DataIO):

    def __init__(self):
        super().__init__()

        self.status = status_none
        self.solver = ""
        self.charges = [0]
        self.discharges = [0]
        self.socs = [0]
        self.agg_battery_demands = [0]
        self.num_intervals_hour = 0

    def results_to_dict_and_dataframe(self, batteries, forecast_demands,
                                      charges, discharges, socs, agg_battery_demands):
        self.charges = charges
        self.discharges = discharges
        self.socs = socs
        self.agg_battery_demands = agg_battery_demands

        self.lists_to_dict(batteries, forecast_demands)
        self.dict_to_dataframe()

    def lists_to_dict(self, batteries, forecasts):
        self.data_dict = dict()
        for battery_name, ch, disch, soc in \
                zip(batteries.data_dict.keys(), self.charges, self.discharges, self.socs):
            self.data_dict[battery_name] = dict()
            self.data_dict[battery_name][d_datetime] = \
                [x.strftime('%Y-%m-%d %H:%M') for x in forecasts.data_df.index]
            self.data_dict[battery_name][t_utc] = [x for x in forecasts.data_df.index \
                .tz_localize(pytz.timezone("Australia/Melbourne")) \
                .tz_convert(pytz.UTC).strftime('%Y-%m-%d %H:%M')]
            self.data_dict[battery_name][b_charges] = list(ch)
            self.data_dict[battery_name][b_discharges] = list(disch)
            self.data_dict[battery_name][b_soc] = list(soc)
        self.data_dict[b_agg_demands] = list(self.agg_battery_demands)

    def dict_to_dataframe(self):
        dict_of_df = {k: pd.DataFrame(v) for k, v in self.data_dict.items()}
        new_schedules = pd.concat(dict_of_df, axis=1)
        for col_name in new_schedules.columns:
            if d_datetime in col_name:
                if d_datetime not in new_schedules:
                    new_schedules[d_datetime] = pd.to_datetime(new_schedules[col_name])
                new_schedules = new_schedules.drop(columns=col_name)
            if t_utc in col_name:
                new_schedules = new_schedules.drop(columns=col_name)

        new_schedules.columns = [' '.join(map(str, col)).strip() if b_agg_demands not in col else b_agg_demands
                                 for col in new_schedules.columns.values]
        # new_schedules[t_utc] = new_schedules[d_datetime].dt.tz_localize(pytz.timezone("Australia/Melbourne")).dt.tz_convert(pytz.UTC).dt.strftime('%Y-%m-%d %H:%M')
        self.data_df = new_schedules.set_index(d_datetime)

        return self.data_df
