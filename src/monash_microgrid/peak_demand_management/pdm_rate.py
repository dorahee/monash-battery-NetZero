from src.monash_microgrid.common.param import *
from src.monash_microgrid.data import dataIO
from src.monash_microgrid.peak_demand_management import payable_dates as dates


class DemandCharge(dataIO.DataIO):

    def __init__(self):
        super().__init__()
        self.new_thresholds = dict()

    def new(self, rate_name, rate, months, times):
        self.data_dict[rate_name] = dict()
        self.data_dict[rate_name][r_rate] = rate
        self.data_dict[rate_name][r_demand_threshold] = 0
        self.data_dict[rate_name][r_months] = months
        self.data_dict[rate_name][r_times] = times
        self.len_data = len(self.data_dict)
        print(rate_name, "is added.")

    def update_thresholds(self, actual_demands, observation_time):
        first_payable_dates = dates.find_first_payable_dates(observation_time, self)
        # print(first_payable_dates)
        for n in self.data_dict.keys():
            new_threshold = 0
            existing_threshold = self.data_dict[n][r_demand_threshold]
            if actual_demands.data_df.size > 0:
                first_payable_date = first_payable_dates[n]
                payable_dates_filter \
                    = (actual_demands.data_df.index >= first_payable_date) & (
                        actual_demands.data_df.index <= observation_time)
                payable_historic_demands \
                    = actual_demands.data_df[payable_dates_filter]. \
                    between_time(f"{self.data_dict[n][r_times][0]}:00",
                                 f"{self.data_dict[n][r_times][-1] - 1}:59")[d_demand]
                if payable_historic_demands.size > 0:
                    new_threshold = payable_historic_demands.max()
                    # print("new t", new_threshold)
                else:
                    existing_threshold = 0

            new_threshold = max(new_threshold, existing_threshold)
            self.new_thresholds[n] = dict()
            self.new_thresholds[n][r_demand_threshold] = new_threshold
            self.data_dict[n][r_demand_threshold] = new_threshold
