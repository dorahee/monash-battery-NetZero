import pandas as pd
from src.monash_microgrid.common.param import *
from src.monash_microgrid.data import dataIO


class Battery(dataIO.DataIO):

    def __init__(self):
        super().__init__()
        self.aggregate_demand = []
        self.soc_full = True

    def new(self, init_cap, min_cap, max_cap, power, eff, battery_name):
        self.data_dict[battery_name] = dict()
        self.data_dict[battery_name][b_init_soc] = init_cap
        self.data_dict[battery_name][b_max_powers] = power
        self.data_dict[battery_name][b_min_soc] = min_cap
        self.data_dict[battery_name][b_max_soc] = max_cap
        self.data_dict[battery_name][b_effs] = eff
        self.len_data = len(self.data_dict)
        print(battery_name, "is added. ")

    def update_initial_socs(self, schedules, start_time):

        dates_filter = (schedules.data_df.index > (start_time - pd.Timedelta(days=2))) & \
                       (schedules.data_df.index <= start_time)
        filtered_schedules = schedules.data_df[dates_filter]

        for n in self.data_dict.keys():

            for col in schedules.data_df.columns.values:
                if f"{n} {b_soc}" in col and schedules.data_df[col].size > 0:
                    soc = float(filtered_schedules[col].values[-1])
                    updated_init_energy = soc
                    self.data_dict[n][b_init_soc] = updated_init_energy

                    if updated_init_energy < 0:
                        print("err")

        if schedules.status is status_updated:
            print("Battery energy levels", [x[b_init_soc] for x in self.data_dict.values()])
        # else:
        #     print("Battery energy levels unchanged. ")
