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
            var float: eod_energy = sum(b in BATTERIES) ((max_energy_capacities[b] - soc[b, end_of_day_interval]));
            var float: demand_charge = sum(r in RATES) (max_demands[r] * charge_thresholds[r]);
            var float: obj = demand_charge + battery_health + eod_energy;
            solve minimize obj;