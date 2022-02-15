from src.monash_battery import load, tracker, visualiser
from src.monash_battery.costs import charge
from src.monash_battery.assets import battery
from src.monash_battery.peak_demand_management import scheduler
import pandas as pd


def main(solver):

    print("--------------------")
    print(solver, "solver is used.")
    print("--------------------")

    batteries = battery.Battery()
    batteries.update(name="Li-on", init_cap=134, min_cap=0, max_cap=134, power=120, eff=0.88)
    batteries.update(name="VFB", init_cap=900, min_cap=0, max_cap=900, power=180, eff=0.65)
    print("--------------------")

    charges = charge.DemandCharge()
    charges.update(name="annual_charge", rate=131.7, months=[i for i in range(1, 13)], times=[x for x in range(7, 20)])
    charges.update(name="summer_charge", rate=162.5, months=[11, 12, 1, 2, 3], times=[15, 16, 17, 18])
    print("--------------------")

    file_forecast = "data/frits/forecast.csv"
    forecast_loads = load.Forecast()
    forecast_loads.new_dataset(file_name=file_forecast)

    file_historical = "data/frits/actual.csv"
    historical_loads = load.Historical()
    historical_loads.new_dataset(file_name=file_historical)
    print("--------------------")

    current_start_time = pd.to_datetime("2020-11-20 00:00")
    previous_start_time = current_start_time
    reschedule_frequency = pd.Timedelta(minutes=1440)
    f_loads = forecast_loads

    solutions_tracker = tracker.Tracker()
    battery_scheduler = scheduler.PeakDemandScheduler()
    battery_scheduler.add_inputs(batteries=batteries, demand_charges=charges, solver=solver)
    while current_start_time.year < 2021:
        if forecast_loads.read_forecast_loads(start_time=current_start_time):
            print(current_start_time)

            solutions_tracker.save_forecast(loads=f_loads)
            battery_scheduler.add_loads(loads=f_loads)
            battery_scheduler.manage_peak_demand(start_time=current_start_time)
            solutions_tracker.save_new_schedules(scheduler=battery_scheduler, freq=reschedule_frequency)

            if previous_start_time is not current_start_time:
                historical_loads.read_historical_loads(start_time=previous_start_time, reschedule_freq=reschedule_frequency)
                solutions_tracker.save_historical(loads=historical_loads)
                solutions_tracker.save_thresholds(charges=charges, previous_time=previous_start_time, current_time=current_start_time)

            charges.update_thresholds(tracker=solutions_tracker)
            batteries.update_initial_socs(tracker=solutions_tracker)

        previous_start_time = current_start_time
        current_start_time = current_start_time + reschedule_frequency

    vis = visualiser.Visualiser()
    vis.add_inputs(tracker=solutions_tracker)
    vis.save_to_csv()
    vis.save_to_graphs()


main(solver="mip")
