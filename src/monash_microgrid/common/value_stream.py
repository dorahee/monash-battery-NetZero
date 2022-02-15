# This file provides the interface for accessing each key function in the battery scheduling algorithm
from src.monash_microgrid.common.param import *
from src.monash_microgrid.visualiser import tracker, visualiser
from src.monash_microgrid.data import time_series_data as tsd
from src.monash_microgrid.assets import battery
from src.monash_microgrid.demand_response import dr_scheduler, dr_rate, dr_baseline


# check if the json strings or json files are provided
def check_input(json_str, json_file, n):
    assert json_str is not json_file, f"Please provide the {n} json string or file."


class ValueStream:

    def __init__(self):
        self.batteries = battery.Battery()

        self.forecast_demands = tsd.TimeSeriesData()
        self.actual_demands = tsd.TimeSeriesData()

        self.forecast_prices = tsd.TimeSeriesData()
        self.actual_prices = tsd.TimeSeriesData()

        self.tracker = tracker.Tracker()
        self.solver = ""

    def save_results_tracker(self, scheduler, rates, tracker_json, tracker_file_name, data_folder):

        forecasts = self.forecast_demands.data_df
        if not self.forecast_prices.data_df.empty:
            forecasts = forecasts.join(self.forecast_prices.data_df)
        self.tracker.read(json_str=tracker_json, folder=data_folder, file_name=tracker_file_name)
        self.tracker.save(schedules=scheduler.data_df,
                          rates=rates,
                          forecasts=forecasts,
                          actual_demands=self.actual_demands.data_df)
        updated_tracker_json = self.tracker.dict_to_json_file(folder=data_folder, file_name=tracker_file_name)
        return updated_tracker_json

    def visualise_results(self, data_folder, file_name, note):
        vis = visualiser.Visualiser()
        vis.add_results(self.tracker)
        vis.write(output_folder=data_folder, file_name=file_name, note=note)
