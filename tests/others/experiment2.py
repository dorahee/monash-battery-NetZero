import input, pandas as pd
from monash_battery import dataset, visualiser, tracker, operation as opt


def main():
    data_folder = "data"
    batteries_json, batteries_json_file, charges_json, charges_json_file, \
    previous_solutions_json, previous_solutions_json_file, loads_json_file, solver \
        = input.input_parameters(folder=data_folder)

    file_forecast = f"{data_folder}/frits/forecast.csv"
    # file_forecast = f"{data_folder}/frits/actual.csv"
    file_historical = f"{data_folder}/frits/actual.csv"
    datasets = dataset.LoadDataSet()
    datasets.data_file(forecast_file_name=file_forecast, historical_file_name=file_historical)

    current_start_time = pd.to_datetime("2020-12-1 00:00")
    frequency = pd.Timedelta(minutes=120)
    previous_start_time = current_start_time - frequency
    while current_start_time.year < 2021:
        if datasets.read_loads(current_start_time=current_start_time,
                               previous_start_time=previous_start_time,
                               freq=frequency):

            loads_json = datasets.to_json_file(loads_json_file)

            # All Ayesha needs
            batteries_json, charges_json, previous_solutions_json = \
                opt.operation(batteries_json=batteries_json, batteries_json_file=batteries_json_file,
                              charges_json=charges_json, charges_json_file=charges_json_file,
                              loads_json=loads_json, loads_json_file=loads_json_file,
                              previous_solutions_json=previous_solutions_json,
                              previous_solutions_json_file=previous_solutions_json_file,
                              solver=solver)

        previous_start_time = current_start_time
        current_start_time = current_start_time + frequency

    vis = visualiser.Visualiser(output_folder="results")
    solutions = tracker.Tracker()
    if previous_solutions_json != "":
        solutions.from_json(previous_solutions_json)
    vis.add_inputs(solutions_tracker=solutions)
    vis.save_to_csv()
    vis.save_to_graphs()


main()
