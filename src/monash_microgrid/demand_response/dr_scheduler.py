from src.monash_microgrid.assets import battery_scheduler
from src.monash_microgrid.demand_response.dr_model import *


class DRScheduler(battery_scheduler.BatteryScheduler):

    def __init__(self, eod_energy_weight, battery_health_weight):
        super().__init__()

        self.eod_energy_weight = eod_energy_weight
        self.battery_health_weight = battery_health_weight

    def optimise(self, batteries, rates, solver, baseline_demands, forecast_demands, forecast_prices,
                 load_reduction_value, loss_factor):
        trigger_price = rates.data_df.loc[r_rate][0]
        dr_intervals = list((forecast_prices.data_df[d_price] >= trigger_price).values * 1)
        dr_prices = [x * y for x, y in zip(forecast_prices.data_df[d_price].values, dr_intervals)]
        dr_demands = [x * y for x, y in zip(forecast_demands.data_df[d_demand].values, dr_intervals)]
        dr_baselines = [x * y for x, y in zip(list(baseline_demands.values()), dr_intervals)]
        # dr_baselines = list(baseline_demands.values())
        eod_index = forecast_demands.eod_index + 1

        if sum(dr_prices) > 0:
            charges, discharges, socs, agg_battery_demands = \
                schedule_batteries(
                    num_intervals_hour=int(forecast_demands.num_intervals_hour),
                    num_intervals_horizon=int(forecast_demands.num_intervals_horizon),
                    forecast_demands=dr_demands,
                    baseline_demands=dr_baselines,
                    forecast_prices=dr_prices,
                    batteries=batteries,
                    solver=solver,
                    eod_index=eod_index,
                    eod_energy_weight=self.eod_energy_weight,
                    battery_health_weight=self.battery_health_weight,
                    load_reduction_value=load_reduction_value,
                    loss_factor=loss_factor)
            self.status = status_updated
        else:
            discharges = [[0] * forecast_demands.num_intervals_horizon] * batteries.len_data
            charges = discharges
            socs = [[b[b_init_soc]] * forecast_demands.num_intervals_horizon for b in batteries.data_dict.values()]
            agg_battery_demands = [0] * forecast_demands.num_intervals_horizon
            self.status = status_unchanged

        self.results_to_dict_and_dataframe(batteries, forecast_demands,
                                           charges, discharges, socs, agg_battery_demands)
        True
