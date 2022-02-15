import pandas as pd
from src.monash_microgrid.common.param import *

folder_name = "pdm_results/"
folder_name = "pdm_data/frits/"
s = "Dec-02_19-06-22-results"
s = "actual_copy"
file_name = f"{s}.csv"

df = pd.read_csv(folder_name + file_name)
df[d_datetime] = pd.to_datetime(df[d_datetime])
df = df.set_index(d_datetime)

df_annual = df.between_time('7:00', '19:00')
df_monthly = df.between_time("15:00", "18:00")
df_month_jan = df_monthly.loc["2020-1-1":"2020-2-1"]
df_month_feb = df_monthly.loc["2020-2-1":"2020-3-1"]
df_month_mar = df_monthly.loc["2020-3-1":"2020-4-1"]
df_month_nov = df_monthly.loc["2020-11-1":"2020-12-1"]
df_month_dec = df_monthly.loc["2020-12-1":"2021-1-1"]


def extract_max(col_ann_name, col_summer_name):
    max_annual = max(df_annual[col_ann_name])
    max_jan = max(df_month_jan[col_summer_name]) if df_month_jan.size > 0 else 0
    max_feb = max(df_month_feb[col_summer_name]) if df_month_feb.size > 0 else 0
    max_mar = max(df_month_mar[col_summer_name]) if df_month_mar.size > 0 else 0
    max_nov = max(df_month_nov[col_summer_name]) if df_month_nov.size > 0 else 0
    max_dec = max(df_month_dec[col_summer_name]) if df_month_dec.size > 0 else 0

    return [max_annual, max_jan, max_feb, max_mar, max_nov, max_dec]


print("                 ", "Annual", "Jan", "Feb", "Mar", "Nov", "Dec")
annual_charge = 131.7
summer_charge = 162.5

f_demand = "forecast demands"
forecast_maxes = extract_max(f_demand, f_demand)
forecast_charges = [round(x * annual_charge / 1000.0, 2) if i == 0 else round(x * summer_charge / 1000.0, 2)
                    for i, x in enumerate(forecast_maxes)]
print("Forecast charges ", forecast_charges)


# annual_threshold = "annual_charge threshold"
# summer_threshold = "summer_charge threshold"
# optimised_maxes = extract_max(annual_threshold, summer_threshold)
# optimised_charges = [round(x * annual_charge / 1000.0, 2) if i == 0 else round(x * summer_charge / 1000.0, 2)
#                      for i, x in enumerate(optimised_maxes)]
# demand_improvement = [round((x - y) / x, 2) if x != 0 else 0
#                       for x, y in zip(forecast_maxes, optimised_maxes)]
# cost_improvement = [round((x - y) / x, 2) if x != 0 else 0
#                     for x, y in zip(forecast_charges, optimised_charges)]
# print("Optimised charges", optimised_charges)
# print("Cost improvement ", cost_improvement)
