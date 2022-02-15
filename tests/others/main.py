from src.monash_battery import dataset, visualiser, tracker
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
    file_forecast = "data/frits/actual.csv"
    file_historical = "data/frits/actual.csv"
    datasets = dataset.LoadDataSet()
    datasets.data_file(forecast_file_name=file_forecast, historical_file_name=file_historical)
    print("--------------------")

    current_start_time = pd.to_datetime("2020-12-1 00:00")
    frequency = pd.Timedelta(minutes=30)
    previous_start_time = current_start_time - frequency

    solutions = tracker.Tracker()
    service = scheduler.PeakDemandScheduler()
    while current_start_time.year < 2021:
        if datasets.read_demands(current_start_time=current_start_time,
                                 previous_start_time=previous_start_time,
                                 horizon_start_time_limit="6:00", horizon_end_time_limit="18:00",
                                 freq=frequency):
            print("--------------------")
            print(current_start_time)
            service.optimise(batteries=batteries, rates=charges, solver=solver, loads=datasets)
            solutions.save(scheduler=service,
                           loads=datasets,
                           rates=charges,
                           previous_time=previous_start_time,
                           current_time=current_start_time)
            charges.update_thresholds(tracker=solutions)
            batteries.update_initial_socs(tracker=solutions)

        previous_start_time = current_start_time
        current_start_time = current_start_time + frequency

    vis = visualiser.Visualiser()
    vis.add_inputs(tracker=solutions)
    vis.save_to_csv()
    vis.save_to_graphs()


main(solver="mip")
