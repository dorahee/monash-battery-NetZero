# This file provides the interface for accessing each key function in the battery scheduling algorithm
from src.monash_microgrid.common.param import *
from src.monash_microgrid.common import value_stream
from src.monash_microgrid.demand_response import dr_scheduler, dr_rate, dr_baseline


# check if the json strings or json files are provided
def check_input(json_str, json_file, n):
    assert json_str is not json_file, f"Please provide the {n} json string or file."


class DRStream(value_stream.ValueStream):

    def __init__(self):
        super().__init__()
        self.rates = dr_rate.DemandResponseRate()
        self.dr_scheduler = dr_scheduler.DRScheduler(eod_energy_weight=10, battery_health_weight=1)

    def run(self,
            demand_forecasts_json, demand_forecasts_file_name,
            actual_demands_json, actual_demands_file_name,

            price_forecasts_json, price_forecasts_file_name,
            actual_prices_json, actual_prices_file_name,

            batteries_json, batteries_file_name,
            rates_json, rates_file_name,
            schedule_json, schedule_file_name,
            tracker_json, tracker_file_name,

            solver, observation_time, data_folder,
            max_temperature_forecast, load_reduction_value=0.6, loss_factor=1):

        # -------------------- read batteries, rates and forecasts  --------------------#
        result_status = status_unchanged
        updated_schedules_json = schedule_json
        updated_tracker_json = tracker_json

        # read the forecast demands and prices
        if self.forecast_demands.read(json_str=demand_forecasts_json,
                                      folder=data_folder,
                                      file_name=demand_forecasts_file_name) and \
                self.forecast_prices.read(json_str=price_forecasts_json,
                                          folder=data_folder,
                                          file_name=price_forecasts_file_name):

            # read the DR trigger price and battery details
            if self.rates.read(json_str=rates_json,
                               folder=data_folder,
                               file_name=rates_file_name) and \
                    self.batteries.read(json_str=batteries_json,
                                        folder=data_folder,
                                        file_name=batteries_file_name):
                self.rates.update_trigger_price()

                # read the historic demands
                if self.actual_demands.read(json_str=actual_demands_json,
                                            folder=data_folder,
                                            file_name=actual_demands_file_name):

                    # calculate the baseline demand for the duration of the forecasts
                    forecast_baseline_demands = dr_baseline.baseline_demand(forecast_demands=self.forecast_demands,
                                                                            actual_demands=self.actual_demands,
                                                                            max_temperature=max_temperature_forecast)
                else:
                    forecast_baseline_demands = dr_baseline.baseline_demand(forecast_demands=self.forecast_demands,
                                                                            actual_demands=None,
                                                                            max_temperature=max_temperature_forecast)
                    print("Warning: The actual demands are not read or found. The baseline load is set to zero. ")

                # read the historic prices
                # if not self.actual_prices.read(json_str=actual_prices_json,
                #                                folder=data_folder,
                #                                file_name=actual_prices_file_name):
                #     print("Warning: The actual prices are not read or found. "
                #           "The past DR events cannot be identified using historic prices. ")

                # -------------------- run demand response using the forecast demands and prices --------------------#

                self.solver = solver
                self.dr_scheduler.optimise(batteries=self.batteries, rates=self.rates, solver=self.solver,
                                           baseline_demands=forecast_baseline_demands,
                                           forecast_demands=self.forecast_demands,
                                           forecast_prices=self.forecast_prices,
                                           load_reduction_value=load_reduction_value,
                                           loss_factor=loss_factor)
                result_status = self.dr_scheduler.status
                updated_schedules_json \
                    = self.dr_scheduler.dict_to_json_file(folder=data_folder, file_name=schedule_file_name)

                # -------------------- save and visualise results --------------------#
                updated_tracker_json = self.save_results_tracker(scheduler=self.dr_scheduler,
                                                                 rates=self.rates,
                                                                 tracker_json=tracker_json,
                                                                 tracker_file_name=tracker_file_name,
                                                                 data_folder=data_folder)
                self.visualise_results(data_folder=data_folder, file_name="dr_graph", note="")

            else:
                print("The batteries or the demand response rates are not read or found. "
                      "Please check the input data. ")

        else:
            print("The forecast is not read or found. Please check the input data. "
                  "No new actions are scheduled for batteries")

        return updated_schedules_json, updated_tracker_json, result_status
