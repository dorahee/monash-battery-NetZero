# this script generates the forecast demands and the actual demands for experiments
import pandas as pd
from src.monash_microgrid.data import dataIO, demand_dataset
from src.monash_microgrid.common.param import *


class FritsDemandForecasts(demand_dataset.DemandDataSet):

    def __init__(self):
        super().__init__()

    def read_demands(self, demand_type, previous_battery_aggregate_power,
                     observation_time, horizon_end_time,
                     horizon_start_time_limit, horizon_end_time_limit):

        self.observation_time = observation_time
        self.start_time = observation_time + pd.Timedelta(minutes=self.minutes_interval)
        self.end_time = horizon_end_time

        self.data_dict = dict()
        self.data_dict[d_datetime] = dict()
        self.data_dict[d_datetime][d_value] \
            = pd.date_range(start=self.start_time, end=horizon_end_time, freq=f"{self.minutes_interval}min")
        self.data_dict[d_datetime][d_freq] = self.minutes_interval

        self.data_dict[d_demand] = dict()
        self.data_dict[d_consumption] = dict()
        df = self.dataset_df[self.dataset_df.index == pd.to_datetime(observation_time)]
        if df.size > 0:
            new_consumptions = list(df.values[0][:self.data_dict[d_datetime][d_value].size])
            self.data_dict[d_demand][d_value] = [l * self.num_intervals_hour for l in new_consumptions]
            self.data_dict[d_demand][d_unit] = d_kw
            self.data_dict[d_demand][d_type] = demand_type

            self.data_dict[d_consumption][d_value] = new_consumptions
            self.data_dict[d_consumption][d_unit] = d_kwh
            self.data_dict[d_consumption][d_type] = demand_type

            return True
        else:
            return False

        # for testing
        # True


class FritsHistoricDemands(demand_dataset.DemandDataSet):

    def __init__(self):
        super().__init__()

    def read_demands(self, demand_type, previous_battery_aggregate_power,
                     observation_time, horizon_end_time,
                     horizon_start_time_limit, horizon_end_time_limit):

        col_datetime = self.col_timestamp
        if col_datetime in self.dataset_df:
            self.dataset_df = self.dataset_df.set_index(col_datetime)

        col_consumption = self.col_consumption

        # # apply the battery schedule to the actual demands
        # if len(previous_battery_aggregate_power) > 0:
        #     for d, p in zip(previous_battery_aggregate_power[d_datetime],
        #                     previous_battery_aggregate_power[b_agg_demands]):
        #         if d in self.dataset_df.index:
        #             self.dataset_df.loc[d, d_demand] = self.dataset_df.loc[d, col_loads] * self.num_intervals_hour + p
        # else:
        #     self.dataset_df[d_demand] = self.dataset_df[col_loads] * self.num_intervals_hour

        # apply the battery schedule to the actual demands
        if previous_battery_aggregate_power.size > 0:
            if "actual" in demand_type:
                self.dataset_df.update(previous_battery_aggregate_power)
                self.dataset_df[d_demand] \
                    = self.dataset_df[col_consumption] * self.num_intervals_hour + self.dataset_df[b_agg_demands]
                True
            # if max(self.dataset_df[d_demand]) > 10000:
            #     print(max(self.dataset_df[d_demand]))
            # self.dataset_df[d_consumption] \
            #     = self.dataset_df[col_consumption] + self.dataset_df[b_agg_demands] / self.num_intervals_hour
        else:
            self.dataset_df[b_agg_demands] = 0
            self.dataset_df[d_demand] = self.dataset_df[col_consumption] * self.num_intervals_hour
            self.dataset_df[d_consumption] = self.dataset_df[col_consumption]

        self.observation_time = observation_time
        self.start_time = observation_time + pd.Timedelta(minutes=self.minutes_interval)
        df = self.dataset_df[self.start_time: horizon_end_time]. \
            between_time(horizon_start_time_limit, horizon_end_time_limit, include_start=True, include_end=False)
        # df[d_demand] = [l * self.num_intervals_hour for l in list(df[col_loads])]

        if df.size > 0:
            self.data_dict = dict()
            self.data_dict[d_datetime] = dict()
            self.data_dict[d_datetime][d_value] = pd.to_datetime(df.index.values)
            self.data_dict[d_datetime][d_freq] = self.minutes_interval

            self.data_dict[d_demand] = dict()
            self.data_dict[d_demand][d_value] = list(df[d_demand].values)
            self.data_dict[d_demand][d_unit] = d_kw
            self.data_dict[d_demand][d_type] = demand_type

            self.data_dict[d_consumption] = dict()
            self.data_dict[d_consumption][d_value] = list(df[d_consumption].values)
            self.data_dict[d_consumption][d_unit] = d_kwh
            self.data_dict[d_consumption][d_type] = demand_type

            return True
        else:
            return False

        # for testing
        # True
