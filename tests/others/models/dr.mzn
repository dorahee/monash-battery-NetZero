% Use this editor as a MiniZinc scratch book
int: num_intervals;
int: num_intervals_hour;
int: eod_index;
set of int: INTERVALS = 1..num_intervals;

% batteries
int: num_batteries;
set of int: BATTERIES = 1..num_batteries;

array[BATTERIES] of float: init_socs; % in kwh
array[BATTERIES] of float: min_socs; % in kwh
array[BATTERIES] of float: max_socs; % in kwh
array[BATTERIES] of float: max_powers;
float: power_limit = max(max_powers);
array[BATTERIES] of float: efficiencies;

% forecasts
array[INTERVALS] of float: forecast_demands;
float: demand_limit;
array[INTERVALS] of float: baseline_demands;
array[INTERVALS] of float: forecast_prices;

% dr rates
float: load_reduction_value;
float: loss_factor;

% decision variables
array[BATTERIES, INTERVALS] of var 0..power_limit: charges;
array[BATTERIES, INTERVALS] of var - power_limit..0: discharges;
array[BATTERIES, INTERVALS] of var float: soc;
array[INTERVALS] of var
0..demand_limit: modified_demands = array1d([forecast_demands[i] +
                                             sum(b in BATTERIES)(charges[b, i] + discharges[b, i]) | i in INTERVALS]);

% either charge or discharge constraint
constraint forall(b in BATTERIES, i in INTERVALS)(charges[b, i] * discharges[b, i] = 0);

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

% socdynamics
constraint forall(b in BATTERIES, i in 2..num_intervals)
(soc[b, i] * num_intervals_hour - soc[b, i - 1] * num_intervals_hour =
charges[b, i] * efficiencies[b] + discharges[b, i]);

% objective: battery health
float: battery_health_weight;
var float: battery_health = sum(b in BATTERIES, i in INTERVALS)(charges[b, i]);

% objective: end of day energy level
float: eod_energy_weight;
var float: eod_energy = sum(b in BATTERIES)(max_socs[b] - soc[b, eod_index]);

% objective: dr returns
var float: dr_returns = - sum(i in INTERVALS)
(forecast_prices[i] * (baseline_demands[i] - modified_demands[i]) * load_reduction_value * loss_factor);

% objective: the combined cost
var float: obj = dr_returns + battery_health * battery_health_weight + eod_energy * eod_energy_weight;

solve
minimize
obj;