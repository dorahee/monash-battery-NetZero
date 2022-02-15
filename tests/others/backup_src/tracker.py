from src.monash_battery.param import *
import pandas as pd
from calendar import monthrange


class Tracker:

    def __init__(self):
        self.minute_interval = 0
        self.num_intervals_day = 0
        self.num_intervals_year = 0

        self.all_demands = pd.DataFrame()

        self.current_schedule = pd.DataFrame()
        self.all_schedules = pd.DataFrame()

        self.current_forecast = pd.DataFrame()
        self.all_forecasts = pd.DataFrame()

        self.current_historical = pd.DataFrame()
        self.all_historical = pd.DataFrame()

        self.current_thresholds = pd.DataFrame()
        self.all_thresholds = pd.DataFrame()

    def save_new_schedules(self, scheduler, reschedule_freq):
        self.minute_interval = scheduler.forecasts.minutes_interval
        self.num_intervals_day = scheduler.forecasts.num_intervals_day

        day_schedule = pd.DataFrame()
        day_schedule[d_datetime] = pd.date_range(start=scheduler.current_start_time,
                                                 periods=self.num_intervals_day,
                                                 freq=f"{self.minute_interval}min")

        for n, ch, dis, soc in zip(scheduler.storages.storages.keys(), scheduler.charges,
                                   scheduler.discharges, scheduler.socs):
            day_schedule[f"{n}_{b_charges}"] = ch
            day_schedule[f"{n}_{b_discharges}"] = dis
            day_schedule[f"{n}_{b_soc}"] = soc
            # day_schedule[n, b_charges] = ch
            # day_schedule[n, b_discharges] = dis
            # day_schedule[n, b_soc] = soc
        day_schedule[b_agg_demands] = scheduler.agg_battery_demands

        reschedule_freq_to_minutes = sum([x * y for x, y in zip(reschedule_freq.components[:4], [24 * 60, 60, 1])])
        no_decisions_to_execute = int(reschedule_freq_to_minutes / self.minute_interval)
        self.current_schedule = day_schedule[:no_decisions_to_execute]
        self.all_schedules = self.all_schedules.append(self.current_schedule)

    def save_forecast(self, forecast):
        forecast_demands = pd.DataFrame()
        forecast_demands[d_datetime] = forecast.demands[d_datetime]
        forecast_demands[d_forecast_original] = forecast.demands[d_demand]
        self.current_forecast = forecast_demands
        self.all_forecasts = self.all_forecasts.append(forecast_demands)

    def save_historical(self, historical):
        historical_demands = pd.DataFrame()
        historical_demands[d_datetime] = historical.demands[d_datetime]
        historical_demands[d_historical_original] = historical.demands[d_demand]
        historical_demands = pd.merge(historical_demands, self.all_schedules[[d_datetime, b_agg_demands]], on=d_datetime, how="inner")
        historical_demands[d_historical_modified] = historical_demands[d_historical_original] + historical_demands[b_agg_demands]
        self.current_historical = historical_demands
        self.all_historical = self.all_historical.append(historical_demands)

    def save_actual(self, actual):
        True

    def combine_demands(self):
        self.all_historical[d_datetime] = pd.to_datetime(self.all_historical[d_datetime])
        self.all_forecasts[d_datetime] = pd.to_datetime(self.all_forecasts[d_datetime])
        self.all_thresholds[d_datetime] = pd.to_datetime(self.all_thresholds[d_datetime])
        self.all_demands = pd.merge(self.all_historical, self.all_forecasts, on=d_datetime)
        self.all_demands = pd.merge(self.all_demands, self.all_thresholds, on=d_datetime)

    def save_thresholds(self, charges, previous_time, current_time):

        current_month = current_time.month
        previous_month = previous_time.month
        self.current_thresholds = pd.DataFrame()
        self.num_intervals_year = 365 * 24 * 60 / self.minute_interval
        new_threshold2 = max(self.current_historical[d_historical_modified])

        for n in charges.demand_charges.keys():
            col_name = (n, r_demand_threshold)
            self.current_thresholds[d_datetime] = self.current_historical[d_datetime]

            if col_name in self.all_thresholds.columns:

                new_threshold = new_threshold2
                if "summer" in n:
                    if current_month in charges.demand_charges[n][r_months] and previous_month is current_month:
                        num_past_values = -previous_time.day
                        threshold_past = max(self.all_thresholds[col_name].values[: num_past_values])
                    else:
                        threshold_past = 0
                        new_threshold = 0
                else:
                    last_day_current_month = monthrange(current_time.year, current_month)[1]
                    last_date_current_month = f"{current_time.year}-{current_month}-{last_day_current_month}"
                    annual_horizon = pd.date_range(end=last_date_current_month, freq="M", periods=12)
                    annual_charge_horizon_start_date = f"{annual_horizon[0].year}-{annual_horizon[0].month}-{1}"
                    print(annual_charge_horizon_start_date)
                    date_times = pd.date_range(start=annual_charge_horizon_start_date, freq="D", end=current_time)
                    num_past_values = -date_times.size \
                        if len(self.all_thresholds) > self.num_intervals_year else self.all_thresholds.size
                    threshold_past = max(self.all_thresholds[col_name].values[: num_past_values])

                self.current_thresholds[col_name] = max(new_threshold, threshold_past)
            else:
                self.current_thresholds[col_name] = new_threshold2

        self.all_thresholds = self.all_thresholds.append(self.current_thresholds)
