from src.monash_microgrid.common.param import *
from src.monash_microgrid.peak_demand_management import payable_dates as dates
from src.monash_microgrid.data import dataIO


class Threshold(dataIO.DataIO):

    def __init__(self):
        super().__init__()

    def update(self, charges, actual_demands, current_date_time):

        first_payable_dates = dates.find_first_payable_dates(current_date_time, self)
        new_thresholds = dict()

        for n in charges.data_dict.keys():
            if actual_demands.data_df.size > 0:
                first_payable_date = first_payable_dates[n]
                payable_dates_filter \
                    = (actual_demands.data_df.index >= first_payable_date) & (
                            actual_demands.data_df.index <= current_date_time)
                payable_historic_demands = actual_demands.data_df[payable_dates_filter][d_demand]
                new_threshold = payable_historic_demands.max() if payable_historic_demands.size > 0 else 0
            else:
                new_threshold = 0
            new_thresholds[n] = new_threshold

        self.data_dict = new_thresholds

# payable_dates = (self.all_thresholds.index >= first_payable_date) \
#                 & (self.all_thresholds.index <= current_time)
# previous_thresholds = self.all_thresholds[payable_dates]
# existing_threshold \
#     = max(previous_thresholds[col_name].values) if previous_thresholds.size > 0 else 0

# def new(self, charges, current_time):
#        self.thresholds = pd.DataFrame()
#        self.thresholds.index.name = d_datetime
#        for n in charges.demand_charges.keys():
#            existing_threshold = charges.demand_charges[n][r_demand_threshold]
#            col_name = f"{n} {r_demand_threshold}"
#            self.thresholds.loc[current_time, col_name] = existing_threshold

#     payable_times = charges.demand_charges[n][r_times]
#     payable_periods_demands = actuals_history.between_time(f"{payable_times[0]}:00",
#                                                            f"{payable_times[-1]}:00")
#     new_threshold = max(payable_periods_demands[d_demand].values)
#     existing_threshold = 0
#
#     # if this charge has a threshold already, look at the previous thresholds
#     col_name = f"{n} {r_demand_threshold}"
#     if col_name not in thresholds_history.columns:
#         pass
#     else:
#         # first payable date for the annual demand charge
#         current_month_last_day = monthrange(current_year, current_month)[1]
#         current_month_last_date = f"{current_year}-{current_month}-{current_month_last_day}"
#         payable_dates_filter = pd.date_range(end=current_month_last_date, freq="M", periods=12)
#         first_payable_date = f"{payable_dates_filter[0].year}-{payable_dates_filter[0].month}-1"
#
#         # first payable date for the summer demand charge
#         if "summer" in n:
#             if current_month in charges.demand_charges[n][r_months] and previous_month is current_month:
#                 first_payable_date = f"{current_year}-{current_month}-1"
#             else:
#                 new_threshold = 0
#
#         payable_dates = (thresholds_history.index >= first_payable_date) & (
#                 thresholds_history.index <= current_time)
#         previous_thresholds = thresholds_history[payable_dates]
#         if previous_thresholds.size > 0:
#             existing_threshold = max(previous_thresholds[col_name].values)
#
#     thresholds[col_name] = max(new_threshold, existing_threshold)
#
#
# thresholds = thresholds.set_index(d_datetime)
