from src.monash_microgrid.data import dataIO
from src.monash_microgrid.common.param import *
import pandas as pd


class Tracker(dataIO.DataIO):

    def __init__(self):
        super().__init__()

    def save(self, rates, forecasts, actual_demands, schedules):

        if d_price in forecasts.columns:
            # forecasts[d_price] = pd.to_numeric(forecasts[d_price])
            forecasts.rename(columns={d_price: f"{d_forecast_original} {d_price}"}, inplace=True)
        new_data_df = forecasts.join(schedules)
        new_data_df.rename(columns={d_demand: f"{d_forecast_original} {d_demand}"}, inplace=True)

        if self.data_df.empty:
            # set the historic demand to be zero
            new_data_df[f"{d_actual_original} {d_demand}"] = 0
            self.data_df = new_data_df

            # initialise the demand thresholds for each charge if applicable
            if hasattr(rates, "new_thresholds"):
                for k in rates.new_thresholds.keys():
                    col_threshold = f"{k} {r_demand_threshold}"
                    self.data_df[col_threshold] = 0

            if hasattr(rates, r_trigger_price):
                self.data_df[r_trigger_price] = rates.trigger_price

            self.data_df = self.data_df.reset_index()
            self.data_dict = self.data_df.to_dict(orient="list")
        else:

            # update the values in the dataset
            for row in new_data_df.iterrows():
                i = row[0]
                if i not in self.data_df.index:
                    self.data_df.loc[i] = row[1]
                else:
                    self.data_df.loc[i, :] = row[1]

            # update the demand thresholds if applicable
            if hasattr(rates, "new_thresholds"):
                for k in rates.new_thresholds.keys():
                    col_threshold = f"{k} {r_demand_threshold}"
                    for t in new_data_df.index:
                        self.data_df.loc[t, col_threshold] = rates.new_thresholds[k][r_demand_threshold]
                        # if min(charges.data_dict[k][r_times]) <= t.hour < max(charges.data_dict[k][r_times]):
                        #     self.data_df.loc[t, col_threshold] = charges.new_thresholds[k][r_demand_threshold]
                        # else:
                        #     self.data_df.loc[t, col_threshold] = 0

            if hasattr(rates, r_trigger_price):
                self.data_df[r_trigger_price] = rates.trigger_price

            # update the actual demands
            actual_demands_df = actual_demands.rename(columns={d_demand: f"{d_actual_original} {d_demand}"})
            self.data_df.update(actual_demands_df)
            self.data_df = self.data_df.fillna(0)
            self.data_df = self.data_df.reset_index()
            self.data_dict = self.data_df.to_dict(orient="list")

# for c in new_data_df.columns:
#     self.data_df.loc[i, c] = row[1][c]
# if i in self.data_df.index:
#     pass
# else:
#     self.data_df.loc[i] = row[1]
# self.data_df[f"{d_actual_original} {d_demand}"]
# = self.data_df[f"{d_actual_original} {d_demand}"].fillna(0)
# self.data_df[t_utc] = self.data_df[d_datetime]\
#     .dt.tz_localize(pytz.timezone("Australia/Melbourne"))\
#     .dt.tz_convert(pytz.UTC).dt.strftime('%Y-%m-%d %H:%M')
# print(self.data_df)
# class Tracker(dataIO.DataIO):
#
#     def __init__(self):
#         super().__init__()
#         self.minute_interval = 0
#         # self.num_intervals_day = 0
#         self.num_intervals_hour = 0
#         self.num_intervals_horizon = 0
#
#         self.new_schedules = pd.DataFrame()
#         self.new_forecasts = pd.DataFrame()
#         self.new_actuals = pd.DataFrame()
#         self.new_thresholds = pd.DataFrame()
#
#         self.schedules_history = pd.DataFrame()
#         self.forecasts_history = pd.DataFrame()
#         self.actuals_history = pd.DataFrame()
#         self.thresholds_history = pd.DataFrame()
#         self.demands_history = pd.DataFrame()
#
#         self.solution_status = status_updated
#
#     def from_json(self, json_str):
#         tracker = json.loads(json_str)
#         self.schedules_history = pd.DataFrame.from_dict(tracker[t_schedules])
#         self.schedules_history[d_datetime] = pd.to_datetime(self.schedules_history[d_datetime])
#         self.schedules_history = self.schedules_history.set_index(d_datetime)
#
#         self.forecasts_history = pd.DataFrame.from_dict(tracker[t_forecasts])
#         self.forecasts_history[d_datetime] = pd.to_datetime(self.forecasts_history[d_datetime])
#         self.forecasts_history = self.forecasts_history.set_index(d_datetime)
#
#         self.actuals_history = pd.DataFrame.from_dict(tracker[t_actual])
#         self.actuals_history[d_datetime] = pd.to_datetime(self.actuals_history[d_datetime])
#         self.actuals_history = self.actuals_history.set_index(d_datetime)
#
#         self.thresholds_history = pd.DataFrame.from_dict(tracker[t_thresholds])
#         self.thresholds_history[d_datetime] = pd.to_datetime(self.thresholds_history[d_datetime])
#         self.thresholds_history = self.thresholds_history.set_index(d_datetime)
#
#     def to_json(self):
#         tracker_dict = dict()
#         tracker_dict[t_schedules] = self.schedules_history.reset_index().to_dict(orient="list")
#         tracker_dict[t_forecasts] = self.forecasts_history.reset_index().to_dict(orient="list")
#         tracker_dict[t_actual] = self.actuals_history.reset_index().to_dict(orient="list")
#         tracker_dict[t_thresholds] = self.thresholds_history.reset_index().to_dict(orient="list")
#
#         def convert_datetime(key):
#             if d_datetime in tracker_dict[key]:
#                 tracker_dict[key][d_datetime] \
#                     = [x if type(x) is str else x.strftime('%Y-%m-%d %H:%M') for x in tracker_dict[key][d_datetime]]
#
#         convert_datetime(t_schedules)
#         convert_datetime(t_forecasts)
#         convert_datetime(t_actual)
#         convert_datetime(t_thresholds)
#
#         tracker_json = json.dumps(tracker_dict)
#         return tracker_json
#
#     def consolidate(self):
#         self.forecasts_history.rename(columns={d_demand:f"forecast {d_demand}"}, inplace=True)
#         self.forecasts_history = self.forecasts_history.drop(columns=d_unit)
#
#         self.actuals_history.rename(columns={d_demand:f"actual {d_demand}"}, inplace=True)
#         self.actuals_history = self.actuals_history.drop(columns=d_unit)
#
#         self.demands_history = self.actuals_history.join([self.forecasts_history, self.thresholds_history])
#         self.demands_history = self.demands_history.drop_duplicates()
#
#     def save(self, schedules, forecasts, actuals, thresholds):
#         self.minute_interval = forecasts.minutes_interval
#         self.num_intervals_hour = int(60 / self.minute_interval)
#         self.num_intervals_horizon = forecasts.num_intervals_horizon
#
#         self.__save_schedules(schedules=schedules)
#         self.__save_forecasts(forecasts=forecasts)
#         self.__save_actuals(actuals=actuals)
#         self.__save_thresholds(thresholds=thresholds)
#         True
#
#     def __save_schedules(self, schedules):
#
#         self.new_schedules = schedules.to_dataframe()
#         # update the schedule history
#         if self.schedules_history.size > 0:
#             for row in self.new_schedules.iterrows():
#                 i = row[0]
#                 if i in self.schedules_history.index:
#                     self.schedules_history.loc[i, :] = row[1]
#                 else:
#                     self.schedules_history.loc[i] = row[1]
#         else:
#             self.schedules_history = self.schedules_history.append(self.new_schedules)
#
#         # print("Schedules are saved. ")
#
#     def __save_forecasts(self, forecasts):
#
#         self.new_forecasts = forecasts.data_df
#         if self.forecasts_history.size > 0:
#             for row in self.new_forecasts.iterrows():
#                 i = row[0]
#                 if i in self.forecasts_history.index:
#                     self.forecasts_history.loc[i, :] = row[1]
#                 else:
#                     self.forecasts_history.loc[i] = row[1]
#         else:
#             self.forecasts_history = self.forecasts_history.append(self.new_forecasts)
#
#         # print("Forecasts are saved. ")
#
#     def __save_actuals(self, actuals):
#
#         if self.actuals_history.size > 0:
#             self.new_actuals = actuals.demands
#             self.new_actuals = self.new_actuals.join(self.schedules_history[b_agg_demands], how="inner")
#             for row in self.new_actuals.iterrows():
#                 i = row[0]
#                 if i in self.actuals_history.index:
#                     self.actuals_history.loc[i, :] = row[1]
#                 else:
#                     self.actuals_history.loc[i] = row[1]
#         else:
#             self.new_actuals = pd.DataFrame(self.new_forecasts.index)
#             self.new_actuals[d_demand] = 0
#             self.new_actuals = self.new_actuals.set_index(d_datetime)
#             self.new_actuals = self.new_actuals.join(self.schedules_history[b_agg_demands], how="inner")
#             self.actuals_history = self.actuals_history.append(self.new_actuals)
#
#         # print("Actual demands are saved. ")
#
#     def __save_thresholds(self, thresholds):
#
#         self.new_thresholds = thresholds.thresholds
#         if self.thresholds_history.size > 0:
#             for row in self.new_thresholds.iterrows():
#                 i = row[0]
#                 if i in self.thresholds_history.index:
#                     self.thresholds_history.loc[i, :] = row[1]
#                 else:
#                     self.thresholds_history.loc[i] = row[1]
#         else:
#             self.thresholds_history = self.thresholds_history.append(self.new_thresholds)
#
#         # print("Thresholds are saved. ")
#
