# parameters for batteries
name = "battery_name"
b_min_soc = "min_soc"
b_max_soc = "max_soc"
b_max_powers = "max_power"
b_effs = "efficiency"
b_init_soc = "init_soc"
b_eod_soc = "end_of_day_soc"
b_charges = "charges"
b_discharges = "discharges"
b_agg_demands = "aggregate_powers"
b_soc = "socs"
b_num_batteries = "num_batteries"
b_schedules = "schedules"

# parameters for time series data (demands and prices)
d_datetime = "timestamps"
d_price = "prices"
d_demand = "demands"
d_data = "data"
d_name = "name"
d_consumption = "consumptions"
d_unit = "unit"
d_kw = "kw"
d_kwh = "kwh"
d_dollar_kw = "dollar_kw"
d_dollar_kwh = "dollar_kwh"
d_freq = "frequency_minutes"
d_value = "values"
d_type = "type"
d_actual_original = "actual"
d_actual_modified = "actual_modified"
d_actual_max_original = "actual_max_original"
d_actual_max_modified = "actual_max_modified"
d_forecast_original = "forecast"
d_forecast_optimised = "forecast_optimised"
d_forecast_max_original = "forecast_max"
d_forecast_max_optimised = "forecast_max_optimised"

# parameters for peak demand rates
r_annual_max = "annual"
r_summer_max = "summer"
r_rate = "charge_rate"
r_months = "months"
r_demand_threshold = "threshold"
r_charge_name = "charge_name"
r_cycle_start_month = "begin_cycle_month"
r_times = "times"
r_trigger_price = "trigger_price"

# parameters for scheduler
status_updated = "threshold_updated"
status_unchanged = "threshold_unchanged"
status_none = "threshold_none"
dr_LRV = 0.6

# parameters for trackers
t_schedules = "all_schedules"
t_forecasts = "all_forecasts"
t_actual = "all_actuals"
t_thresholds = "all_thresholds"
t_utc = "utc"

# file names
f_actual_demand = "demand_actual"
f_demand_forecast = "demand_forecasts"
f_actual_price = "price_actual"
f_price_forecast = "price_forecasts"
f_charge = "charges"
f_battery = "batteries"
f_schedule = "schedules"
f_tracker = "tracker"
f_threshold = "thresholds"

# parameters for demand response
num_like_days = 10

