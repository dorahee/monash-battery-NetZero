from minizinc import *
import numpy as np
from src.monash_microgrid.common.param import *


def schedule_batteries(num_intervals_horizon, num_intervals_hour,
                       forecast_demands, baseline_demands, forecast_prices,
                       batteries, solver,
                       eod_index, eod_energy_weight, battery_health_weight,
                       load_reduction_value, loss_factor):
    model = Model()
    model.add_string(make_model())
    mip_solver = Solver.lookup(solver)
    ins = Instance(mip_solver, model)

    # time parameters
    ins["num_intervals"] = num_intervals_horizon
    ins["num_intervals_hour"] = num_intervals_hour
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

    # forecasts
    ins["forecast_demands"] = [float(x) for x in forecast_demands]
    ins["baseline_demands"] = [float(x) for x in baseline_demands]
    ins["forecast_prices"] = [float(x) for x in forecast_prices]
    ins["demand_limit"] = float(max(forecast_demands) * 999)

    # dr prices
    ins["load_reduction_value"] = load_reduction_value
    ins["loss_factor"] = loss_factor

    # objective weights
    ins["eod_energy_weight"] = eod_energy_weight
    ins["battery_health_weight"] = battery_health_weight

    try:
        results = ins.solve()
        charges = np.array(results.solution.charges).round(2)
        discharges = np.array(results.solution.discharges).round(2)
        socs = np.array(results.solution.soc).round(2)
    except:
        print()

    # actual demand from charging
    actual_charged_demands = [np.array(x) for x, eff in zip(charges, efficiencies)]
    actual_discharged_demands = [np.array(x) for x, eff in zip(discharges, efficiencies)]
    total_charged_demands = np.array(actual_charged_demands).sum(axis=0)
    total_discharged_demands = np.array(actual_discharged_demands).sum(axis=0)
    aggregate_battery_demands = total_charged_demands + total_discharged_demands

    return charges, discharges, socs, aggregate_battery_demands


def make_model():
    str_model = """
    % ---------- Input parameters ---------- %
    
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

        % forecasts
        array[INTERVALS] of float: forecast_demands;
        float: demand_limit;
        array[INTERVALS] of float: baseline_demands;
        array[INTERVALS] of float: forecast_prices;

        % dr charges
        float: load_reduction_value;
        float: loss_factor;
    
    % ---------- Variables ---------- %
    
        % decision variables
        array[BATTERIES, INTERVALS] of var 0..power_limit: charges;
        array[BATTERIES, INTERVALS] of var -power_limit..0: discharges;
        array[BATTERIES, INTERVALS] of var float: soc;
        array[INTERVALS] of var 0..demand_limit: modified_demands = array1d([forecast_demands[i] + 
        sum(b in BATTERIES)(charges[b, i] + discharges[b, i])| i in INTERVALS]);
        array[INTERVALS] of var 0..1: dr_min_reduction;

    % ---------- Constraints ---------- %
    
        % Charge or discharge only constraint
        constraint forall(b in BATTERIES, i in INTERVALS)(charges[b, i] * discharges[b, i] = 0);

        % Maximum power constraints
        constraint forall(b in BATTERIES, i in INTERVALS)(discharges[b, i] <= 0.0);
        constraint forall(b in BATTERIES, i in INTERVALS)(discharges[b, i] >= -max_powers[b]);

        constraint forall(b in BATTERIES, i in INTERVALS)(charges[b, i] <= max_powers[b]);
        constraint forall(b in BATTERIES, i in INTERVALS)(charges[b, i] >= 0);
        % at least 1kw reduction. 

        % Maximum-minmum capacity constraints
        constraint forall(b in BATTERIES, i in INTERVALS)(soc[b, i] <= max_socs[b]);
        constraint forall(b in BATTERIES, i in INTERVALS)(soc[b, i] >= min_socs[b]);

        % SOC constraints
        constraint forall(b in BATTERIES)
        (soc[b, 1] * num_intervals_hour - init_socs[b] * num_intervals_hour = 
            charges[b, 1] * efficiencies[b] + discharges[b, 1]);

        constraint forall(b in BATTERIES, i in 2..num_intervals) 
            (soc[b, i] * num_intervals_hour - soc[b, i - 1] * num_intervals_hour = 
        charges[b, i] * efficiencies[b] + discharges[b, i]);
        
        % DR minimum reduction constraint
        constraint forall(i in INTERVALS) (
        dr_min_reduction[i] = ((baseline_demands[i] - modified_demands[i]) > 1.0 )
        );

    % ---------- Objectives ---------- % 
    
        % objective: battery health
        float: battery_health_weight;
        var float: battery_health = sum(b in BATTERIES, i in INTERVALS)(charges[b, i]);
        
        % objective: end of day energy level
        float: eod_energy_weight;
        var float: eod_energy = sum(b in BATTERIES) (max_socs[b] - soc[b, eod_index]);
        
        % objective: dr returns
        var float: dr_returns = - sum(i in INTERVALS) 
          ( forecast_prices[i] * ( baseline_demands[i] - modified_demands[i] ) * dr_min_reduction[i] * 
          load_reduction_value * loss_factor );
        % var float: dr_returns = - sum(i in INTERVALS) 
        %   (forecast_prices[i] * reduced_demands[i] * load_reduction_value * loss_factor);
        
        % objective: the combined cost
        var float: obj = dr_returns + battery_health * battery_health_weight + eod_energy * eod_energy_weight;
        
        solve minimize obj;
    """

    return str_model

