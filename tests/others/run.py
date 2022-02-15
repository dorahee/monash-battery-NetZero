from tests.others.scripts import scheduler, charge, solution, asset
from tests.others.scripts import load
import pandas as pd


def main(solver):
    # step 1: add batteries
    batteries = asset.Battery()
    batteries.new(name="Li-on", init_cap=134, min_cap=0, max_cap=134, power=120, eff=0.88)
    batteries.new(name="VFB", init_cap=900, min_cap=0, max_cap=900, power=180, eff=0.65)
    print("--------------------")

    # step 2: add peak demand charges
    charges = charge.DemandCharge()
    charges.new(name="annual_charge", rate=131.7, cycle_start_month=1, months=[i for i in range(1, 13)])
    charges.new(name="summer_charge", rate=162.5, cycle_start_month=12, months=[12, 1, 2])
    print("--------------------")

    # # step 3: read historic loads as the actual loads
    file_historical_loads = "data/historic_loads.csv"
    i_col_historical_loads = 3
    file_forecast_loads = "data/historic_loads.csv"
    i_col_forecast_loads = 3

    historical_loads_type = l_frits_historical
    file_historical_loads = "data/frits/actual.csv"
    i_col_historical_loads = 1

    # Frits forecast data
    forecast_loads_type = l_frits_historical
    forecast_loads_type = l_frits_forecast
    if forecast_loads_type is l_frits_forecast:
        file_forecast_loads = "data/frits/forecast.csv"
        data_header = None
    else:
        file_forecast_loads = "data/frits/actual.csv"
        data_header = "infer"

    i_col_forecast_loads = 1
    loads = load.Loads()
    loads.new_historical_loads(file_name=file_historical_loads, i_col_loads=i_col_historical_loads)
    loads.new_forecast_loads(file_name=file_forecast_loads, i_col_loads=i_col_forecast_loads,
                             forecast_type=forecast_loads_type, header=data_header)
    print("--------------------")

    # step 4: daily schedule
    optimiser = scheduler.BatteryScheduler()
    sol = solution.Solution()
    next_start_time = pd.to_datetime("2020-12-1 00:00")
    current_start_time = next_start_time
    time_horizon = pd.Timedelta(days=1)
    reschedule_frequency = pd.Timedelta(minutes=1440)
    while next_start_time.year < 2021:

        # step 4.1: reset the demand thresholds if needed
        charges.reset_demand_thresholds(current_time_step=current_start_time, next_time_step=next_start_time)

        # step 4.2: move to the next time step
        current_start_time = next_start_time
        current_end_time = current_start_time + time_horizon

        # step 4.3: update the initial energy levels for batteries
        batteries.update_init_energy_levels(optimiser=optimiser, start_time=current_start_time)

        # step 4.4: read the load forecasts
        if loads.read_forecast_loads(start_time=current_start_time, end_time=current_end_time,
                                     loads_type=forecast_loads_type):

            # step 4.5: use the optimiser
            optimiser.peak_demand_management(loads=loads,
                                             batteries=batteries,
                                             peak_demand_charges=charges,
                                             current_time_step=current_start_time,
                                             solver=solver)

            # step 4.6: set the next start time
            next_start_time = current_start_time + reschedule_frequency

            # step 4.7: save the solution between current start time and the next start time
            if loads.read_historical_loads(start_time=current_start_time, end_time=next_start_time,
                                           unit="kw", loads_type=historical_loads_type):
                sol.save_current_solution(loads=loads,
                                          optimiser=optimiser,
                                          peak_demand_charges=charges,
                                          next_start_time=next_start_time,
                                          current_start_time=current_start_time)
            else:
                continue
        else:
            next_start_time = current_start_time + reschedule_frequency

    sol.draw_all_solutions()


main(solver="gurobi")
