# This file provides the interface for accessing each key function in the battery scheduling algorithm
from src.monash_microgrid.common.param import *
from src.monash_microgrid.common import value_stream
from src.monash_microgrid.visualiser import tracker, visualiser
from src.monash_microgrid.data import time_series_data as tsd
from src.monash_microgrid.assets import battery
from src.monash_microgrid.peak_demand_management import pdm_scheduler, pdm_rate


# check if the json strings or json files are provided
def check_input(json_str, json_file, n):
    assert json_str is not json_file, f"Please provide the {n} json string or file."


class PDMStream(value_stream.ValueStream):

    def __init__(self):
        super().__init__()
        self.rates = pdm_rate.DemandCharge()
        self.pdm_scheduler = pdm_scheduler.PDMScheduler(eod_energy_weight=10, battery_health_weight=1)

    def run(self, forecasts_json, forecasts_file_name,
            actual_json, actual_file_name,
            batteries_json, batteries_file_name,
            charges_json, charges_file_name,
            schedule_json, schedule_file_name,
            tracker_json, tracker_file_name,
            solver, observation_time, data_folder):

        # -------------------- read batteries, rates and forecasts  --------------------#
        result_status = status_unchanged
        updated_schedules_json = schedule_json
        updated_tracker_json = tracker_json
        updated_charges_json = charges_json

        if self.forecast_demands.read(json_str=forecasts_json,
                                      folder=data_folder,
                                      file_name=forecasts_file_name):
            if self.rates.read(json_str=charges_json,
                               folder=data_folder,
                               file_name=charges_file_name) and \
                    self.batteries.read(json_str=batteries_json,
                                        folder=data_folder,
                                        file_name=batteries_file_name):

                # -------------------- update demand thresholds based on historic demands --------------------#
                check_input(schedule_json, schedule_file_name, "last schedule")

                if self.actual_demands.read(json_str=actual_json,
                                            folder=data_folder,
                                            file_name=actual_file_name):
                    self.rates.update_thresholds(actual_demands=self.actual_demands,
                                                 observation_time=self.forecast_demands.start_date_time)
                    updated_charges_json = self.rates.dict_to_json_file(folder=data_folder,
                                                                        file_name=charges_file_name)
                    # for testing
                    # self.rates.from_json_file(folder=data_folder, file_name=charges_file_name)

                else:
                    updated_charges_json = charges_json
                    print("Warning: the actual demands are not read or found. ")

                # -------------------- manage peak demand using the forecast demands --------------------#

                self.solver = solver
                self.pdm_scheduler.optimise(batteries=self.batteries,
                                            rates=self.rates,
                                            forecast_demands=self.forecast_demands,
                                            solver=solver)
                result_status = self.pdm_scheduler.status
                updated_schedules_json = self.pdm_scheduler.dict_to_json_file(folder=data_folder,
                                                                              file_name=schedule_file_name)
                # for testing
                # self.service.from_json_file(folder=data_folder, file_name=schedule_file_name)

                # -------------------- save and visualise results --------------------#
                updated_tracker_json = self.save_results_tracker(scheduler=self.pdm_scheduler,
                                                                 rates=self.rates,
                                                                 tracker_json=tracker_json,
                                                                 tracker_file_name=tracker_file_name,
                                                                 data_folder=data_folder)
                self.visualise_results(data_folder=data_folder, file_name="pdm_graph", note="")

            else:
                print("The batteries or the peak demand charges are not read or found. "
                      "Please check the input data. ")

        else:
            print("The forecast is not read or found. Please check the input data. "
                  "No new actions are scheduled for batteries")

        return updated_schedules_json, updated_tracker_json, updated_charges_json, result_status
