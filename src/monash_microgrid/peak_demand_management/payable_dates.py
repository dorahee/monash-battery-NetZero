import pandas as pd
from calendar import monthrange
from src.monash_microgrid.common.param import *


def find_first_payable_dates(current_date_time, charges):

    first_payable_dates = dict()

    for n in charges.data_dict.keys():

        current_year = current_date_time.year
        current_month = current_date_time.month
        current_month_last_day = monthrange(current_year, current_month)[1]
        current_month_last_date = f"{current_year}-{current_month}-{current_month_last_day}"
        payable_dates_filter = pd.date_range(end=current_month_last_date, freq="M", periods=12)
        payable_time_start = charges.data_dict[n][r_times][0]
        first_payable_date = f"{payable_dates_filter[0].year}-{payable_dates_filter[0].month}-1 {payable_time_start}:00"

        if "summer" in n:
            first_payable_date = f"{current_year}-{current_month}-1 {payable_time_start}:00"

        first_payable_dates[n] = pd.to_datetime(first_payable_date)

    return first_payable_dates
