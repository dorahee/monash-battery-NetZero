% time
int: num_intervals;
int: num_intervals_hour; 
set of int: INTERVALS = 1..num_intervals; 

% batteries
int: num_batteries;
set of int: BATTERIES = 1..num_batteries;

array[BATTERIES] of float: init_energy_levels;  % in kwh
array[BATTERIES] of float: min_energy_capacities;  % in kwh
array[BATTERIES] of float: max_energy_capacities;  % in kwh
array[BATTERIES] of float: max_powers; 
array[BATTERIES] of float: efficiencies;

% demands
float: current_demand_threshold;
array[INTERVALS] of float: load_forecast;
float: demand_limit = 999999999999.9;

% peak demand charges
float: max_demand_charge;

% decision variables
var 0..demand_limit: daily_max_demand; 
array[BATTERIES, INTERVALS] of var float: charges;
array[BATTERIES, INTERVALS] of var float: discharges;
array[BATTERIES, INTERVALS] of var float: soc;
% array[INTERVALS] of var 0..demand_limit: aggregate_battery_profile = 
% array1d([sum(b in BATTERIES)(charges[b, i]/efficiencies[b] + discharges[b, i] * efficiencies[b])
% | i in INTERVALS]);
array[INTERVALS] of var 0..demand_limit: modified_demand = 
array1d([load_forecast[i] * num_intervals_hour + 
sum(b in BATTERIES)(charges[b, i]/efficiencies[b] + discharges[b, i] * efficiencies[b])
| i in INTERVALS]);

% objective
var float: obj = (daily_max_demand - current_demand_threshold) * max_demand_charge;
constraint obj >= 0;

% either charge or discharge constraint
constraint forall(b in BATTERIES, i in INTERVALS) (charges[b, i] * discharges[b, i] = 0);

% charge constraints
constraint forall(b in BATTERIES, i in INTERVALS)
(discharges[b, i] <= 0);
constraint forall(b in BATTERIES, i in INTERVALS)
(discharges[b, i] >= -max_powers[b]);

% discharge constraints
constraint forall(b in BATTERIES, i in INTERVALS)
(charges[b, i] <= max_powers[b]);
constraint forall(b in BATTERIES, i in INTERVALS)
(charges[b, i] >=0);

% soc constraints
constraint forall(b in BATTERIES, i in INTERVALS)
(soc[b, i] <= max_energy_capacities[b]);

constraint forall(b in BATTERIES, i in INTERVALS)
(soc[b, i] >= min_energy_capacities[b]);

% initial soc
constraint forall(b in BATTERIES)
(soc[b, 1] = init_energy_levels[b]);

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

% output [show(existing_demands)];
