from minizinc import *
from src.monash_battery.param import *
import numpy as np
from src.monash_battery import load
from src.monash_battery.costs import charge
from src.monash_battery.assets import battery
from math import ceil


class BatteryScheduler:

    def __init__(self):
        self.status = status_none
        self.batteries = battery.Battery()
        self.demand_charges = charge.DemandCharge()
        self.forecasts = load.Forecast()
        self.solver = ""
        self.current_start_time = 0
        self.current_month = 0
        self.charges = [0] * self.forecasts.num_intervals_day
        self.discharges = [0] * self.forecasts.num_intervals_day
        self.socs = [0] * self.forecasts.num_intervals_day
        self.agg_battery_demands = [0] * self.forecasts.num_intervals_day

    def add_inputs(self, batteries, demand_charges, solver):
        self.batteries = batteries
        self.demand_charges = demand_charges
        self.solver = solver

    def add_forecast_loads(self, forecasts):
        self.forecasts = forecasts

    def manage_peak_demand(self, start_time):
        demand_charges = self.demand_charges
        forecasts = self.forecasts
        current_minute = start_time.hour * 60 + start_time.minute
        current_interval = int(1440 / current_minute) if current_minute > 0 else 0
        horizon_intervals = [x + 1 for x in range(current_interval, self.forecasts.num_intervals_day)] + \
                            [x + 1 for x in range(0, current_interval)]
        current_hour = start_time.hour
        current_month = start_time.month
        self.current_start_time = start_time
        self.current_month = current_month

        charges_rates = []
        charge_times = []
        charge_thresholds = []
        for dc in demand_charges.demand_charges.values():
            charge_thresholds.append(dc[r_demand_threshold])
            charges_rates.append(dc[r_rate] if current_month in dc[r_months] else 0)
            mask_charge_times = [1 if int(ceil(x / forecasts.num_intervals_hour)) - 1 in dc[r_times] else 0 for x in horizon_intervals]
            charge_times.append(mask_charge_times)

        if max(forecasts.demands[d_demand]) > max(charge_thresholds):
            end_day_interval = max(1, (1440 - current_hour * 60 - current_minute) / forecasts.minutes_interval)
            charges, discharges, socs, agg_battery_demands = \
                self.__schedule_batteries(end_of_day_interval=end_day_interval,
                                          charge_rates=charges_rates,
                                          charge_times=charge_times,
                                          charge_thresholds=charge_thresholds)
            self.status = status_updated
        else:
            do_nothing = [[0] * forecasts.num_intervals_day] * self.batteries.num_batteries
            charges = do_nothing
            discharges = do_nothing
            agg_battery_demands = do_nothing[0]
            socs = [[b[b_init_energy]] * forecasts.num_intervals_day for b in self.batteries.storages.values()]
            self.status = status_unchanged

        self.charges = charges
        self.discharges = discharges
        self.socs = socs
        self.agg_battery_demands = agg_battery_demands

    def __schedule_batteries(self, end_of_day_interval, charge_rates, charge_times, charge_thresholds):
        model = Model()
        model.add_string(self.__optimisation_model())
        mip_solver = Solver.lookup(self.solver)
        ins = Instance(mip_solver, model)

        # time parameters
        ins["num_intervals"] = int(self.forecasts.num_intervals_day)
        ins["num_intervals_hour"] = int(self.forecasts.num_intervals_hour)
        ins["end_of_day_interval"] = int(end_of_day_interval)

        # battery parameters
        ins["num_batteries"] = self.batteries.num_batteries
        specs = self.batteries.storages
        ins["init_energy_levels"] = [b[b_init_energy] for b in specs.values()]
        ins["min_energy_capacities"] = [b[b_min_caps] for b in specs.values()]
        ins["max_energy_capacities"] = [b[b_max_caps] for b in specs.values()]
        ins["max_powers"] = [b[b_max_powers] for b in specs.values()]
        efficiencies = [b[b_effs] for b in specs.values()]
        ins["efficiencies"] = efficiencies
        demands = list(self.forecasts.demands[d_demand].values)
        ins["demand_forecast"] = demands
        ins["demand_limit"] = max(demands) * 999
        ins["charge_rates"] = charge_rates
        ins["charge_times"] = charge_times
        ins["charge_thresholds"] = charge_thresholds

        results = ins.solve()
        try:
            socs = np.array(results.solution.soc).round(2)
            charges = np.array(results.solution.charges).round(2)
            discharges = np.array(results.solution.discharges).round(2)
        except:
            False

        # actual demand from charging
        actual_charged_demands = [np.array(x) / eff for x, eff in zip(charges, efficiencies)]
        actual_discharged_demands = [np.array(x) * eff for x, eff in zip(discharges, efficiencies)]
        total_charged_demands = np.array(actual_charged_demands).sum(axis=0)
        total_discharged_demands = np.array(actual_discharged_demands).sum(axis=0)
        aggregate_battery_demands = total_charged_demands + total_discharged_demands

        return charges, discharges, socs, aggregate_battery_demands

    def __optimisation_model(self):
        str_model = """
            % time
            int: num_intervals;
            int: num_intervals_hour; 
            int: end_of_day_interval;
            set of int: INTERVALS = 1..num_intervals; 
            
            % batteries
            int: num_batteries;
            set of int: BATTERIES = 1..num_batteries;
            
            array[BATTERIES] of float: init_energy_levels;  % in kwh
            array[BATTERIES] of float: min_energy_capacities;  % in kwh
            array[BATTERIES] of float: max_energy_capacities;  % in kwh
            array[BATTERIES] of float: max_powers; 
            float: power_limit = max(max_powers);
            array[BATTERIES] of float: efficiencies;
            
            % demands
            array[INTERVALS] of float: demand_forecast;
            float: demand_limit;
            
            % peak demand charges
            array[int] of float: charge_rates;
            array[int] of float: charge_thresholds;
            array[int, INTERVALS] of int: charge_times;
            set of int: RATES = index_set(charge_rates);
            
            % decision variables
            array[RATES] of var 0..demand_limit: max_demands; 
            array[BATTERIES, INTERVALS] of var 0..power_limit: charges;
            array[BATTERIES, INTERVALS] of var -power_limit..0: discharges;
            array[BATTERIES, INTERVALS] of var float: soc;
            array[INTERVALS] of var 0..demand_limit: modified_demand = array1d([demand_forecast[i] + 
            sum(b in BATTERIES)(charges[b, i]/efficiencies[b] + discharges[b, i] * efficiencies[b])| i in INTERVALS]);
                 
            % either charge or discharge constraint
            % constraint forall(b in BATTERIES, i in INTERVALS)(charges[b, i] * discharges[b, i] = 0);
            
            % charge constraints
            constraint forall(b in BATTERIES, i in INTERVALS)(discharges[b, i] <= 0.0);
            constraint forall(b in BATTERIES, i in INTERVALS)(discharges[b, i] >= -max_powers[b]);
            
            % discharge constraints
            constraint forall(b in BATTERIES, i in INTERVALS)(charges[b, i] <= max_powers[b]);
            constraint forall(b in BATTERIES, i in INTERVALS)(charges[b, i] >= 0.0);
            
            % soc constraints
            constraint forall(b in BATTERIES, i in INTERVALS)(soc[b, i] <= max_energy_capacities[b]);
            
            constraint forall(b in BATTERIES, i in INTERVALS)(soc[b, i] >= min_energy_capacities[b]);
            
            % initial soc
            constraint forall(b in BATTERIES)(soc[b, 1] = init_energy_levels[b]);
              
            % soc dynamics
            constraint forall(b in BATTERIES, i in 2..num_intervals) 
            (soc[b, i] * num_intervals_hour - soc[b, i - 1] * num_intervals_hour = 
            charges[b, i - 1] + discharges[b, i - 1]);
                            
            % max demand
            constraint forall(r in RATES, i in INTERVALS)(max_demands[r] >= modified_demand[i] * charge_times[r, i]);
            constraint forall(r in RATES) (max_demands[r] >= charge_thresholds[r]);
            
            % objective
            var float: battery_health = sum(b in BATTERIES, i in INTERVALS)(charges[b, i]);
            var float: eod_energy = sum(b in BATTERIES) (max_energy_capacities[b] - soc[b, end_of_day_interval]) * 10;
            var float: demand_charge = sum(r in RATES) (max_demands[r] * charge_rates[r]);
            var float: obj = demand_charge + battery_health + eod_energy;
            solve minimize obj;
        """

        return str_model


