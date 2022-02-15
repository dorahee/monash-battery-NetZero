import pandas as pd
from src.monash_microgrid.common import monash_holidays
from src.monash_microgrid.common.param import *
from src.monash_microgrid.demand_response import dr_uplift


def dr_event(date_time, actual_demands):
    return False


def like_days_baseline(date_time, actual_demands):
    like_days = dict()
    like_day_date = pd.to_datetime(date_time) - pd.Timedelta(weeks=1)
    # print("-----", " evaluating", date_time)
    while len(like_days) < 10 and like_day_date in actual_demands.data_df.index:
        like_day_demand = actual_demands.data_df.loc[like_day_date][d_demand]

        # check if this date is a Monash work day
        # print(monash_holidays.check_workday(year=like_day_date.year,
        #                                     month=like_day_date.month,
        #                                     day=like_day_date.day))
        if monash_holidays.check_workday(year=like_day_date.year, month=like_day_date.month, day=like_day_date.day):

            # check if this date had a DR event
            if not dr_event(like_day_date, actual_demands):
                like_days[like_day_date] = like_day_demand
                # print(date_time, like_day_date, like_day_demand)

        like_day_date -= pd.Timedelta(days=1)

    if len(like_days) > 0:
        baseline_load = sum(like_days.values())/len(like_days)
    else:
        baseline_load = 0

    return baseline_load


def baseline_demand(forecast_demands, actual_demands, max_temperature):
    forecast_baseline_demands = dict()
    uplift_factors = dr_uplift.TmaxUplift()
    if actual_demands is None:
        for d in forecast_demands.data_df.index:
            forecast_baseline_demands[d] = 0
    else:
        for d in forecast_demands.data_df.index:
            forecast_baseline_demands[d] \
                = like_days_baseline(d, actual_demands) * uplift_factors.read_uplift_factor(max_temperature)

    return forecast_baseline_demands

