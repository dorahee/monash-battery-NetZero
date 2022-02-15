from tests.others.scripts import scheduler, charge, solution, asset
from tests.others.scripts import load
from tests.others.scripts.param import *
import pandas as pd

# step 0: read essential input data
solver = "gurobi"
battery_specs = asset.Battery()
peak_demand_charges = charge.peak_demand_charges()
target_demand_threshold = 0
daily_results_tracker = pd.DataFrame()
for day in range(2, 30):

    # step 1: read net demand data
    # start = f"2021-6-{day} 01:30"
    # end = f"2021-6-{day + 1} 01:30"
    start = pd.Timestamp(f"2021-6-{day} 01:30")
    end = start + pd.Timedelta(days=1)
    file = "data/PRICE_AND_DEMAND_202106_VIC1.csv"
    df = load.read_loads_by_date(file=file, start_date=start, end_date=end)
    df_net_demand = df["TOTALDEMAND"]
    df_dates = df["SETTLEMENTDATE"]
    daily_max_demand = max(df_net_demand)
    num_intervals = len(df_net_demand)
    assert num_intervals == 48, f"Missing data on day {day}"
    print(f"{start} net demand data is read.")

    # step 2: peak demand optimisation
    if daily_max_demand > target_demand_threshold:

        print("Peak demand charge event is triggered. ")
        # run the optimiser
        results = scheduler.schedule_for_peak_demand_management(num_intervals=num_intervals, num_intervals_hour=int(num_intervals / 24),
                                                                current_demand_threshold=target_demand_threshold,
                                                                batteries=battery_specs, charges=peak_demand_charges,
                                                                loads=list(df_net_demand), solver=solver)

        # retrieve results
        target_demand_threshold = results[d_forecast_max_demand_optimised]
        battery_specs[b_init_energy] = results[b_eod_energy]
        print("Target demand threshold: ", round(target_demand_threshold, 2), "kW")

    else:
        print("Peak demand charge event is not triggered. ")
        results = dict()
        results[d_forecast_demand_original] = df_net_demand
        results[d_forecast_demand_optimised] = df_net_demand
        results[d_forecast_max_demand_optimised] = target_demand_threshold
        no_battery_activities = [[0 for i in range(num_intervals)] for _ in range(battery_specs[b_num_batteries])]
        results[b_charges] = no_battery_activities
        results[b_discharges] = no_battery_activities

    # organise results
    df = solution.organise_daily_results(df_dates=df_dates, results=results)
    assert len(df) == len(df_net_demand)
    daily_results_tracker = daily_results_tracker.append(df)

    print("----------")

solution.draw_daily_results(daily_results_tracker)
print("Experiment is completed.")


# -------------------------------------------------------------------------------- #
# todo: 1)skip weekends and public holidays; 2) incorporate summer peak;
