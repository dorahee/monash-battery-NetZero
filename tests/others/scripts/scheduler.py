from minizinc import *
from scripts.param import *
import numpy as np
import pandas as pd


class BatteryScheduler:

    def __init__(self):
        self.solution_df = pd.DataFrame()
        self.status = status_none
        self.selected_solution_df = pd.DataFrame()

    def select_solution(self, next_start_time):
        self.selected_solution_df = self.solution_df[:next_start_time].iloc[:-1]

    def peak_demand_management(self, loads, batteries, peak_demand_charges, current_time_step, solver):

        # read the relevant demand charges and thresholds
        relevant_thresholds = []
        relevant_charges = []
        current_month = current_time_step.month
        for charge, months, threshold in zip(
                peak_demand_charges.demand_charges[r_peak_demand_charge],
                peak_demand_charges.demand_charges[r_months],
                peak_demand_charges.demand_charges[r_demand_threshold]):
            if current_month in months:
                relevant_charges.append(charge)
                relevant_thresholds.append(threshold)
        max_demand_charge = max(relevant_charges)
        min_relevant_demand_threshold = min(relevant_thresholds)

        end_of_day_interval = (1440 - current_time_step.hour * 60 - current_time_step.minute) / loads.minutes_interval
        print(end_of_day_interval)

        # check if the peak demand management event needs to be triggered
        scheduling_horizon_max_demand = max(loads.current_forecast_demands)
        if scheduling_horizon_max_demand > min_relevant_demand_threshold:

            print(scheduling_horizon_max_demand, min_relevant_demand_threshold)
            r_dict = self.__trigger_peak_demand_management(num_intervals_day=loads.num_intervals_day,
                                                           num_intervals_hour=loads.num_intervals_hour,
                                                           current_demand_threshold=min_relevant_demand_threshold,
                                                           solver=solver,
                                                           batteries=batteries.storages,
                                                           max_demand_charge=max_demand_charge,
                                                           demands=loads.current_forecast_demands,
                                                           end_of_day_interval=end_of_day_interval)
            self.status = status_updated
        else:
            r_dict = self.__do_nothing(num_intervals_day=loads.num_intervals_day,
                                       current_demand_threshold=min_relevant_demand_threshold,
                                       batteries=batteries.storages,
                                       demands=loads.current_forecast_demands)
            self.status = status_unchanged

        df = pd.DataFrame()
        df[d_forecast_demand_original] = r_dict[d_forecast_demand_original]
        df[d_forecast_demand_optimised] = r_dict[d_forecast_demand_optimised]
        df[b_agg_demands] = r_dict[b_agg_demands]
        for i, p, ch, dis, soc in zip(batteries.storages[name], batteries.storages[b_max_powers],
                                      r_dict[b_charges], r_dict[b_discharges], r_dict[b_soc]):
            df[i + ": " + b_charges] = ch
            df[i + ": " + b_discharges] = dis
            df[i + ": " + b_soc] = soc
        df.index = loads.current_forecast_datetime_range
        self.solution_df = df

    def __do_nothing(self, num_intervals_day, current_demand_threshold, demands, batteries):

        socs = [[e] * num_intervals_day for e in batteries[b_init_energy]]
        num_batteries = len(socs)
        no_battery_activities = [[0 for _ in range(num_intervals_day)] for _ in range(num_batteries)]

        res_dict = dict()
        res_dict[b_charges] = no_battery_activities
        res_dict[b_discharges] = no_battery_activities
        res_dict[b_soc] = socs
        res_dict[b_agg_demands] = no_battery_activities[0]
        res_dict[d_forecast_demand_original] = demands
        res_dict[d_forecast_demand_optimised] = demands

        return res_dict

    def __trigger_peak_demand_management(self, num_intervals_day, end_of_day_interval,
                                         num_intervals_hour,
                                         current_demand_threshold, demands,
                                         solver, batteries, max_demand_charge):
        model = Model()
        model.add_string(
            """
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
    float: current_demand_threshold;
    array[INTERVALS] of float: demand_forecast;
    float: demand_limit;
    
    % peak demand charges
    float: max_demand_charge;
    
    % decision variables
    var 0..demand_limit: daily_max_demand; 
    array[BATTERIES, INTERVALS] of var 0..power_limit: charges;
    array[BATTERIES, INTERVALS] of var -power_limit..0: discharges;
    array[BATTERIES, INTERVALS] of var float: soc;
    array[INTERVALS] of var 0..demand_limit: modified_demand = 
    array1d([demand_forecast[i] + 
    sum(b in BATTERIES)(charges[b, i]/efficiencies[b] + discharges[b, i] * efficiencies[b])
    | i in INTERVALS]);
    
    % objective
    var float: obj = (daily_max_demand) * max_demand_charge 
    + sum(b in BATTERIES, i in INTERVALS)(charges[b, i])
    + sum(b in BATTERIES) (max_energy_capacities[b] - soc[b, end_of_day_interval]) * max_demand_charge;
        
    % either charge or discharge constraint
    constraint forall(b in BATTERIES, i in INTERVALS) (charges[b, i] * discharges[b, i] = 0);
    
    % charge constraints
    constraint forall(b in BATTERIES, i in INTERVALS)
    (discharges[b, i] <= 0.0);
    constraint forall(b in BATTERIES, i in INTERVALS)
    (discharges[b, i] >= -max_powers[b]);
    
    % discharge constraints
    constraint forall(b in BATTERIES, i in INTERVALS)
    (charges[b, i] <= max_powers[b]);
    constraint forall(b in BATTERIES, i in INTERVALS)
    (charges[b, i] >= 0.0);
    
    % soc constraints
    constraint forall(b in BATTERIES, i in INTERVALS)
    (soc[b, i] <= max_energy_capacities[b]);
    
    constraint forall(b in BATTERIES, i in INTERVALS)
    (soc[b, i] >= min_energy_capacities[b]);
    
    % initial soc
    constraint forall(b in BATTERIES)
    (soc[b, 1] = init_energy_levels[b]);
    
    % final soc
    % constraint forall(b in BATTERIES)
    % (soc[b, num_intervals] = init_energy_levels[b]);
    
    % soc dynamics
    constraint forall(b in BATTERIES, i in 2..num_intervals) 
    (soc[b, i] * num_intervals_hour - soc[b, i - 1] * num_intervals_hour = 
    charges[b, i - 1] + discharges[b, i - 1]);
        
    % max demand
    constraint forall(i in INTERVALS)
    (daily_max_demand >= modified_demand[i]);
    constraint daily_max_demand >= current_demand_threshold;
    
    % solve
    solve minimize obj;
            """
        )
        mip_solver = Solver.lookup(solver)
        ins = Instance(mip_solver, model)

        # time parameters
        ins["num_intervals"] = int(num_intervals_day)
        ins["num_intervals_hour"] = int(num_intervals_hour)
        ins["end_of_day_interval"] = int(end_of_day_interval)

        # battery parameters
        num_batteries = len(batteries[b_min_caps])
        ins["num_batteries"] = num_batteries
        ins["init_energy_levels"] = batteries[b_init_energy]
        ins["min_energy_capacities"] = batteries[b_min_caps]
        ins["max_energy_capacities"] = batteries[b_max_caps]
        ins["max_powers"] = batteries[b_max_powers]
        efficiencies = batteries[b_effs]
        ins["efficiencies"] = efficiencies
        ins["demand_forecast"] = demands
        ins["current_demand_threshold"] = current_demand_threshold
        ins["demand_limit"] = max(demands) * 999

        # peak charges
        ins["max_demand_charge"] = max_demand_charge

        results = ins.solve()
        # try:
        #     results = ins.solve()
        # except:
        #     print("error")

        socs = np.array(results.solution.soc).round(2)
        charges = np.array(results.solution.charges).round(2)
        discharges = np.array(results.solution.discharges).round(2)
        max_demand_threshold = np.round(results.solution.daily_max_demand, 2)

        # actual demand from charging
        actual_demands_from_charging \
            = [np.array(x) / eff for x, eff in zip(charges, efficiencies)]
        actual_demand_from_discharging \
            = [np.array(x) * eff for x, eff in zip(discharges, efficiencies)]

        total_actual_demand_from_charging = np.array(actual_demands_from_charging).sum(axis=0)
        total_actual_demand_from_discharging = np.array(actual_demand_from_discharging).sum(axis=0)
        aggregate_battery_activities = total_actual_demand_from_charging + total_actual_demand_from_discharging

        modified_demand = np.array([d + act for d, act in zip(demands, aggregate_battery_activities)]).round(2)
        if not int(max_demand_threshold) == int(max(modified_demand)):
            print(max_demand_threshold, max(modified_demand))
            print("Modified demand threshold", max(modified_demand))

        res_dict = dict()
        res_dict[b_charges] = charges
        res_dict[b_discharges] = discharges
        res_dict[b_soc] = socs
        res_dict[b_agg_demands] = aggregate_battery_activities
        res_dict[d_forecast_demand_original] = demands
        res_dict[d_forecast_demand_optimised] = modified_demand

        return res_dict
