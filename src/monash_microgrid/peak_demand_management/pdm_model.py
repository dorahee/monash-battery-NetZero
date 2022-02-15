from minizinc import *
import numpy as np
from src.monash_microgrid.common.param import *


def schedule_batteries(forecast_demands, batteries, solver,
                       eod_index, eod_energy_weight, battery_health_weight,
                       charge_rates, charge_times, charge_thresholds):
    model = Model()
    model.add_string(make_model())
    mip_solver = Solver.lookup(solver)
    ins = Instance(mip_solver, model)

    # time parameters
    ins["num_intervals"] = int(forecast_demands.num_intervals_horizon)
    ins["num_intervals_hour"] = int(forecast_demands.num_intervals_hour)
    ins["eod_index"] = int(eod_index)

    # battery parameters
    ins["num_batteries"] = batteries.len_data
    specs = batteries.data_dict
    ins["init_socs"] = [b[b_init_soc] for b in specs.values()]
    ins["min_socs"] = [b[b_min_soc] for b in specs.values()]
    ins["max_socs"] = [b[b_max_soc] for b in specs.values()]
    ins["max_powers"] = [b[b_max_powers] for b in specs.values()]
    efficiencies = [b[b_effs] for b in specs.values()]
    ins["efficiencies"] = [float(x) for x in efficiencies]
    demands = list(forecast_demands.data_df[d_demand].values)
    ins["forecasts"] = [float(x) for x in demands]
    ins["demand_limit"] = float(max(demands) * 999)
    ins["charge_rates"] = [float(x) for x in charge_rates]
    ins["charge_times"] = charge_times
    ins["charge_thresholds"] = [float(x) for x in charge_thresholds]
    ins["eod_energy_weight"] = eod_energy_weight
    ins["battery_health_weight"] = battery_health_weight

    try:
        results = ins.solve()
        discharges = np.array(results.solution.discharges).round(2)
        charges = np.array(results.solution.charges).round(2)
        socs = np.array(results.solution.soc).round(2)
    except:
        print("err")

    # actual demand from charging
    actual_charged_demands = [np.array(x) for x, eff in zip(charges, efficiencies)]
    actual_discharged_demands = [np.array(x) for x, eff in zip(discharges, efficiencies)]
    total_charged_demands = np.array(actual_charged_demands).sum(axis=0)
    total_discharged_demands = np.array(actual_discharged_demands).sum(axis=0)
    aggregate_battery_demands = total_charged_demands + total_discharged_demands

    return charges, discharges, socs, aggregate_battery_demands


def make_model():
    str_model = """
        % time
        int: num_intervals;
        int: num_intervals_hour; 
        int: eod_index;
        set of int: INTERVALS = 1..num_intervals; 

        % batteries
        int: num_batteries;
        set of int: BATTERIES = 1..num_batteries;

        array[BATTERIES] of float: init_socs;  % in kwh
        array[BATTERIES] of float: min_socs;  % in kwh
        array[BATTERIES] of float: max_socs;  % in kwh
        array[BATTERIES] of float: max_powers; 
        float: power_limit = max(max_powers);
        array[BATTERIES] of float: efficiencies;

        % demands
        array[INTERVALS] of float: forecasts;
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
        array[INTERVALS] of var 0..demand_limit: modified_demand = array1d([forecasts[i] + 
        sum(b in BATTERIES)(charges[b, i] + discharges[b, i])| i in INTERVALS]);

        % either charge or discharge constraint
        % constraint forall(b in BATTERIES, i in INTERVALS)(charges[b, i] * discharges[b, i] = 0);

        % charge constraints
        constraint forall(b in BATTERIES, i in INTERVALS)(discharges[b, i] <= 0.0);
        constraint forall(b in BATTERIES, i in INTERVALS)(discharges[b, i] >= -max_powers[b]);

        % discharge constraints
        constraint forall(b in BATTERIES, i in INTERVALS)(charges[b, i] <= max_powers[b]);
        constraint forall(b in BATTERIES, i in INTERVALS)(charges[b, i] >= 0.0);

        % soc constraints
        constraint forall(b in BATTERIES, i in INTERVALS)(soc[b, i] <= max_socs[b]);

        constraint forall(b in BATTERIES, i in INTERVALS)(soc[b, i] >= min_socs[b]);

        % initial soc
        constraint forall(b in BATTERIES)
        (soc[b, 1] * num_intervals_hour - init_socs[b] * num_intervals_hour = 
        charges[b, 1] * efficiencies[b] + discharges[b, 1]);

        % soc dynamics
        constraint forall(b in BATTERIES, i in 2..num_intervals) 
        (soc[b, i] * num_intervals_hour - soc[b, i - 1] * num_intervals_hour = 
        charges[b, i] * efficiencies[b] + discharges[b, i]);

        % max demand
        constraint forall(r in RATES, i in INTERVALS)(max_demands[r] >= modified_demand[i] * charge_times[r, i]);
        constraint forall(r in RATES) (max_demands[r] >= charge_thresholds[r]);

        % objective: battery health
        float: battery_health_weight;
        var float: battery_health = sum(b in BATTERIES, i in INTERVALS)(charges[b, i]);
        
        % objective: end of day energy level
        float: eod_energy_weight;
        % var float: eod_energy = sum(b in BATTERIES) (max_socs[b] - soc[b, eod_index]);
        var float: eod_energy = sum(i in INTERVALS, r in RATES, b in BATTERIES) 
        ((max_socs[b] - soc[b, i]) * (1 - charge_times[r, i]));
        
        % objective: peak demand charge
        var float: demand_charge = sum(r in RATES) (max_demands[r] * charge_rates[r]);
        
        % objective: the combined cost
        var float: obj = demand_charge + battery_health * battery_health_weight + eod_energy * eod_energy_weight;
        
        solve minimize obj;
    """

    return str_model
