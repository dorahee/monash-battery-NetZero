import pandas as pd
import pdm_inputs as data
from datetime import datetime
from src.monash_microgrid.peak_demand_management import pdm_stream
from src.monash_microgrid.visualiser import visualiser
from src.monash_microgrid.common.param import *
from src.monash_microgrid.data import demand


def main():
    # -------------------- input data preparation -------------------- #
    # set the folder for input data
    parent_folder = "tests/"
    parent_folder = ""
    data_folder = f"{parent_folder}pdm_data/"
    result_folder = f"{parent_folder}pdm_results/"

    # generate the input data
    batteries_json, batteries_file_name, \
    charges_json, charges_file_name, \
    forecasts_json, forecasts_file_name, \
    actual_json, actual_file_name, \
    schedule_json, schedule_file_name, \
    tracker_json, tracker_file_name, \
    solver = data.input_parameters(folder=data_folder)
    # thresholds_json, thresholds_file_name, \

    # read the forecast and actual demand data sets
    file_historical = f"{data_folder}frits/actual.csv"
    historical_demands_dataset = demand.FritsHistoricDemands()
    historical_demands_dataset.read_from_csv(file_name=file_historical)

    # forecast_dataset = demand.FritsHistoricDemands()
    # forecast_dataset.read_from_csv(file_name=file_historical)
    file_forecast = f"{data_folder}frits/forecast.csv"
    forecast_dataset = demand.FritsDemandForecasts()
    forecast_dataset.read_from_csv(file_name=file_forecast)

    # -------------------- experiment loops -------------------- #
    # set the date times for starting the experiments
    start_time_limit = "00:00"
    end_time_limit = "23:59"
    observation_time = pd.to_datetime(f"2020-1-1 06:00")
    horizon_end_time = pd.to_datetime(f"{observation_time.year}-{observation_time.month}-{observation_time.day} "
                                      f"{end_time_limit}")
    frequency_minutes = 720
    frequency = pd.Timedelta(minutes=frequency_minutes)
    num_historic_days = 366
    previous_battery_aggregate_power = pd.DataFrame()
    print("--------------------")
    while observation_time.year < 2021:

        print(observation_time, "---", horizon_end_time)
        result_status = status_unchanged

        # -------------------- generate forecast demands -------------------- #
        if forecast_dataset.read_demands(demand_type=d_forecast_original,
                                         previous_battery_aggregate_power=previous_battery_aggregate_power,
                                         observation_time=observation_time, horizon_end_time=horizon_end_time,
                                         horizon_start_time_limit=start_time_limit,
                                         horizon_end_time_limit=end_time_limit):
            forecasts_json = forecast_dataset.dict_to_json_file(folder=data_folder, file_name=f_demand_forecast)

            # -------------------- generate historic demands -------------------- #
            if historical_demands_dataset.read_demands(demand_type=d_actual_original,
                                                       previous_battery_aggregate_power=previous_battery_aggregate_power,
                                                       observation_time=observation_time - pd.Timedelta(
                                                           days=num_historic_days),
                                                       horizon_end_time=observation_time,
                                                       horizon_start_time_limit=start_time_limit,
                                                       horizon_end_time_limit=end_time_limit):
                actual_json = historical_demands_dataset.dict_to_json_file(folder=data_folder,
                                                                           file_name=f_actual_demand)

                # -------------------- schedule the batteries -------------------- #

                # for testing
                # forecast_json = ""
                # forecasts_file_name = ""
                # actual_json = ""
                # actual_file_name = ""
                # batteries_json = ""
                # batteries_file_name = ""
                # charges_json = ""
                # charges_file_name = ""

                # -------------------- All Ayesha needs: start -------------------- #
                opt = pdm_stream.PDMStream()
                schedules_json, tracker_json, charges_json, result_status = \
                    opt.run(batteries_json=batteries_json, batteries_file_name=batteries_file_name,
                            charges_json=charges_json, charges_file_name=charges_file_name,
                            forecasts_json=forecasts_json, forecasts_file_name=forecasts_file_name,
                            actual_json=actual_json, actual_file_name=actual_file_name,
                            tracker_json=tracker_json, tracker_file_name=tracker_file_name,
                            schedule_json=schedule_json, schedule_file_name=schedule_file_name,
                            solver=solver, observation_time=observation_time,
                            data_folder=data_folder)

                # -------------------- All Ayesha needs: end -------------------- #

        observation_time = observation_time + frequency
        if observation_time.hour >= horizon_end_time.hour or observation_time.day != horizon_end_time.day:
            horizon_end_time += pd.Timedelta(hours=24)
            observation_time = horizon_end_time - pd.Timedelta(hours=horizon_end_time.hour - 6,
                                                               minutes=horizon_end_time.minute)
            num_historic_days += 1

        if result_status == status_updated:
            opt.batteries.update_initial_socs(schedules=opt.pdm_scheduler, start_time=observation_time)
            batteries_json = opt.batteries.dict_to_json_file(folder=data_folder, file_name=batteries_file_name)
            previous_battery_aggregate_power = pd.DataFrame(
                {
                    d_datetime: opt.pdm_scheduler.data_df.index,
                    b_agg_demands: opt.pdm_scheduler.agg_battery_demands
                }
            )
            previous_battery_aggregate_power = previous_battery_aggregate_power.set_index(d_datetime)

            print("Battery schedules:", len(opt.pdm_scheduler.agg_battery_demands),
                  list(opt.pdm_scheduler.agg_battery_demands))
            print("Updated thresholds:", opt.rates.new_thresholds)
            print("--------------------")

    vis = visualiser.Visualiser()
    vis.read(json_str=tracker_json, folder=data_folder, file_name=tracker_file_name)
    vis.write(output_folder=result_folder, file_name=datetime.now().strftime("%b-%d_%H-%M-%S") + "-results",
              note=f"{frequency_minutes} mins")
    print("")


main()
