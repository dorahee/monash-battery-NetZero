import pandas as pd
from datetime import datetime

import dr_inputs as data
from src.monash_microgrid.data import demand, price
from src.monash_microgrid.common.param import *
from src.monash_microgrid.demand_response import dr_stream
from src.monash_microgrid.visualiser import visualiser


def main():
    # set the folder for input data
    parent_folder = "tests/"
    parent_folder = ""
    data_folder = f"{parent_folder}dr_data/"
    result_folder = f"{parent_folder}dr_results/"

    # generate the input data
    batteries_json, batteries_file_name, \
    rates_json, rates_file_name, \
    demand_forecast_json, demand_forecast_file_name, \
    actual_demands_json, actual_demands_file_name, \
    price_forecast_json, price_forecast_file_name, \
    actual_prices_json, actual_prices_file_name, \
    schedule_json, schedule_file_name, \
    tracker_json, tracker_file_name, \
    solver = data.input_parameters(folder=data_folder)

    # read the forecast and actual demand data sets
    file_historic_demands = f"{data_folder}frits/actual.csv"
    historic_demands = demand.FritsHistoricDemands()
    historic_demands.read_from_csv(file_name=file_historic_demands)

    demand_forecasts = demand.FritsHistoricDemands()
    demand_forecasts.read_from_csv(file_name=file_historic_demands)

    # file_forecast_demands = f"{data_folder}frits/forecast.csv"
    # demand_forecasts = demand.FritsDemandForecasts()
    # demand_forecasts.read_from_csv(file_name=file_forecast_demands)

    # read the forecast and actual price data sets
    historic_prices = price.HistoricPrices()
    # file_historic_prices = f"{data_folder}frits/dispatch_prices.rds"
    # historic_prices.read_from_rds(data_folder=data_folder, file_name=file_historic_prices)
    file_historic_prices = f"{data_folder}frits/dispatch_prices.csv"
    historic_prices.read_from_csv2(file_name=file_historic_prices)

    prices_forecasts = price.PriceForecasts()
    # file_historic_prices = f"{data_folder}frits/dispatch_prices.rds"
    # historic_prices.read_from_rds(data_folder=data_folder, file_name=file_historic_prices)
    file_forecast_prices = f"{data_folder}frits/vic_predispatch_2019_2020.csv"
    prices_forecasts.read_from_csv(file_name=file_forecast_prices)

    # -------------------- experiment loops -------------------- #
    # set the date times for starting the experiments
    start_time_limit = "00:00"
    end_time_limit = "23:59"
    observation_time = pd.to_datetime(f"2020-12-15 06:00")
    horizon_end_time = pd.to_datetime(f"{observation_time.year}-{observation_time.month}-{observation_time.day} "
                                      f"{end_time_limit}")
    frequency_minutes = pd.Timedelta(minutes=720)
    num_historic_days = 60
    max_historic_days = 366
    previous_battery_aggregate_power = pd.DataFrame()
    print("--------------------")

    while observation_time.year < 2021:

        print(observation_time, "---", horizon_end_time)
        num_historic_days = max(60, num_historic_days)
        result_status = status_unchanged

        # -------------------- generate forecast demands and prices -------------------- #
        if demand_forecasts.read_demands(demand_type=d_forecast_original,
                                         previous_battery_aggregate_power=previous_battery_aggregate_power,
                                         observation_time=observation_time,
                                         horizon_end_time=horizon_end_time,
                                         horizon_start_time_limit=start_time_limit,
                                         horizon_end_time_limit=end_time_limit) and \
                prices_forecasts.read_prices(price_type=d_forecast_original,
                                             observation_time=observation_time,
                                             horizon_end_time=horizon_end_time,
                                             horizon_start_time_limit=start_time_limit,
                                             horizon_end_time_limit=end_time_limit):
            demand_forecast_json = demand_forecasts.dict_to_json_file(folder=data_folder, file_name=f_demand_forecast)
            price_forecast_json = prices_forecasts.dict_to_json_file(folder=data_folder, file_name=f_price_forecast)

            # -------------------- generate historic demands and prices -------------------- #
            historic_data_start_time = observation_time - pd.Timedelta(days=num_historic_days)
            if historic_demands.read_demands(demand_type=d_actual_original,
                                             previous_battery_aggregate_power=previous_battery_aggregate_power,
                                             observation_time=historic_data_start_time,
                                             horizon_end_time=observation_time,
                                             horizon_start_time_limit=start_time_limit,
                                             horizon_end_time_limit=end_time_limit):
                actual_demands_json = historic_demands.dict_to_json_file(folder=data_folder, file_name=f_actual_demand)

                if historic_prices.read_prices(price_type=d_actual_original,
                                               observation_time=historic_data_start_time,
                                               horizon_end_time=observation_time,
                                               horizon_start_time_limit=start_time_limit,
                                               horizon_end_time_limit=end_time_limit):
                    actual_prices_json = historic_prices.dict_to_json_file(folder=data_folder, file_name=f_actual_price)

                # -------------------- schedule the batteries for demand response -------------------- #

                opt = dr_stream.DRStream()
                schedules_json, tracker_json, result_status = \
                    opt.run(batteries_json=batteries_json, batteries_file_name=batteries_file_name,
                            rates_json=rates_json, rates_file_name=rates_file_name,

                            demand_forecasts_json=demand_forecast_json,
                            demand_forecasts_file_name=demand_forecast_file_name,
                            actual_demands_json=actual_demands_json,
                            actual_demands_file_name=actual_demands_file_name,

                            price_forecasts_json=price_forecast_json,
                            price_forecasts_file_name=price_forecast_file_name,
                            actual_prices_json=actual_prices_json,
                            actual_prices_file_name=actual_prices_file_name,

                            tracker_json=tracker_json, tracker_file_name=tracker_file_name,
                            schedule_json=schedule_json, schedule_file_name=schedule_file_name,

                            max_temperature_forecast=37, load_reduction_value=0.6, loss_factor=1,
                            solver=solver, observation_time=observation_time, data_folder=data_folder)

        observation_time = observation_time + frequency_minutes
        if observation_time.hour >= horizon_end_time.hour or observation_time.day != horizon_end_time.day:
            horizon_end_time += pd.Timedelta(hours=24)
            observation_time = horizon_end_time - pd.Timedelta(hours=horizon_end_time.hour - 6,
                                                               minutes=horizon_end_time.minute)
            num_historic_days += 1

        if result_status == status_updated:
            # if True:
            opt.batteries.update_initial_socs(schedules=opt.dr_scheduler, start_time=observation_time)
            batteries_json = opt.batteries.dict_to_json_file(folder=data_folder, file_name=batteries_file_name)
            print("Battery schedules:", len(opt.dr_scheduler.agg_battery_demands),
                  list(opt.dr_scheduler.agg_battery_demands))
            print("--------------------")
        previous_battery_aggregate_power = pd.DataFrame(
            {
                d_datetime: opt.dr_scheduler.data_df.index,
                b_agg_demands: opt.dr_scheduler.agg_battery_demands
            }
        )
        previous_battery_aggregate_power = previous_battery_aggregate_power.set_index(d_datetime)

    vis = visualiser.Visualiser()
    vis.read(json_str=tracker_json, folder=data_folder, file_name=tracker_file_name)
    vis.write(output_folder=result_folder, file_name=datetime.now().strftime("%b-%d_%H-%M-%S") + "-results",
              note=f"{frequency_minutes} mins")
    print("")


main()
