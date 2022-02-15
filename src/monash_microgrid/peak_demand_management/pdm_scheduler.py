from math import floor
from src.monash_microgrid.assets import battery_scheduler
from src.monash_microgrid.peak_demand_management.pdm_model import *


class PDMScheduler(battery_scheduler.BatteryScheduler):

    def __init__(self, eod_energy_weight, battery_health_weight):
        battery_scheduler.BatteryScheduler.__init__(self)

        self.eod_energy_weight = eod_energy_weight
        self.battery_health_weight = battery_health_weight

    def optimise(self, batteries, rates, solver, forecast_demands):

        self.num_intervals_hour = forecast_demands.num_intervals_hour
        horizon_intervals = forecast_demands.horizon_intervals
        eod_index = forecast_demands.eod_index + 1

        charges_rates = []
        charge_times = []
        charge_thresholds = []
        forecast_maxes = []
        current_month = forecast_demands.start_date_time.month
        for dc in rates.data_dict.values():
            if current_month in dc[r_months]:
                charge_times_filter = [1 if int(floor(x / forecast_demands.num_intervals_hour)) in dc[r_times]
                                       else 0 for x in horizon_intervals]
                payable_forecast_max = max(
                    [x * y for x, y in zip(forecast_demands.data_df[d_demand], charge_times_filter)])
                forecast_maxes.append(payable_forecast_max)
                charge_thresholds.append(dc[r_demand_threshold])
                charges_rates.append(dc[r_rate] if current_month in dc[r_months] else 0)
                charge_times.append(charge_times_filter)
                # print(charge_times_filter)

        payable_forecast_thresholds = [1 if x > y else 0 for x, y in zip(forecast_maxes, charge_thresholds)]
        required_batteries = bool(sum(payable_forecast_thresholds) > 0)
        if required_batteries:

            charges, discharges, socs, agg_battery_demands = \
                schedule_batteries(forecast_demands=forecast_demands,
                                   batteries=batteries,
                                   solver=solver,
                                   eod_index=eod_index,
                                   eod_energy_weight=self.eod_energy_weight,
                                   battery_health_weight=self.battery_health_weight,
                                   charge_rates=charges_rates,
                                   charge_times=charge_times,
                                   charge_thresholds=charge_thresholds)
            self.status = status_updated
        else:
            discharges = [[0] * forecast_demands.num_intervals_horizon] * batteries.len_data
            charges = discharges
            socs = [[b[b_init_soc]] * forecast_demands.num_intervals_horizon for b in batteries.data_dict.values()]
            agg_battery_demands = [0] * forecast_demands.num_intervals_horizon
            self.status = status_unchanged

        self.results_to_dict_and_dataframe(batteries, forecast_demands,
                                           charges, discharges, socs, agg_battery_demands)
