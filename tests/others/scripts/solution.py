from pandas_bokeh import *
from bokeh.io import output_file
from bokeh.layouts import column


class Solution:

    def __init__(self):
        self.solutions_tracker = pd.DataFrame()
        self.current_solution = pd.DataFrame()
        self.charge_names = []
        self.max_modified_forecast = 0
        self.max_modified_actual = 0
        self.max_original_actual = 0

    def save_current_solution(self, loads, optimiser, peak_demand_charges, current_start_time, next_start_time):

        if len(loads.current_historical_demands) > 0:


            df2 = optimiser.solution_df
            if next_start_time in df2.index:
                df = df2[:next_start_time].iloc[:-1]
            else:
                df = df2[:len(loads.current_historical_demands)]

            print(list(df2[b_agg_demands]))

            # add historical demands as the actual demand
            df[d_actual_demand_original] = loads.current_historical_demands
            self.max_original_actual = max(loads.current_historical_demands)

            df[d_actual_demand_modified] = df[d_actual_demand_original] + df[b_agg_demands]
            self.max_modified_actual = max(df[d_actual_demand_modified])
            df["temp"] = self.max_modified_actual

            # add the demand thresholds based on the actual demand
            new_demand_thresholds = []
            current_month = current_start_time.month
            for name, months, existing_threshold in zip(peak_demand_charges.demand_charges[r_charge_name],
                                                        peak_demand_charges.demand_charges[r_months],
                                                        peak_demand_charges.demand_charges[r_demand_threshold]):
                if current_month in months:
                    updated_threshold = max(self.max_modified_actual, existing_threshold)
                else:
                    updated_threshold = 0
                new_demand_thresholds.append(updated_threshold)

                df[name + ": " + d_actual_max_demand_modified] = updated_threshold

            peak_demand_charges.demand_charges[r_demand_threshold] = new_demand_thresholds
            print(current_start_time, peak_demand_charges.demand_charges[r_demand_threshold])
            print("--------------------")

            self.solutions_tracker = self.solutions_tracker.append(df)
            self.current_solution = df

    def draw_all_solutions(self):
        self.solutions_tracker.index.name = d_datetime
        df = self.solutions_tracker.reset_index()
        x_ticks = [0] + [i for i in range(1, len(df)) if (i + 1) % 2 == 0]
        df.to_csv("daily_results.csv")

        p_demand_col = [d_datetime]
        p_battery_col = [d_datetime]
        for col in df.columns.values:
            if "demand" in col:
                p_demand_col.append(col)
            if "charges" in col or "soc" in col:
                p_battery_col.append(col)

        plots = []
        fig_size = (1800, 300)
        p_demands = df.loc[:, p_demand_col].plot_bokeh(kind="line", xlabel="Date time", ylabel="Demand (kW)",
                                                       title="Demand (kW)",
                                                       # plot_data_points=True,
                                                       x=d_datetime,
                                                       show_figure=False,
                                                       # xticks=x_ticks,
                                                       figsize=fig_size,
                                                       rangetool=True,
                                                       toolbar_location="above",
                                                       )
        plots.append(p_demands)

        p_batteries = df.loc[:, p_battery_col].plot_bokeh(kind="line", xlabel="Date time", ylabel="Demand (kW)",
                                                          title="Battery activities (kW)",
                                                          # plot_data_points=True,
                                                          x=d_datetime,
                                                          show_figure=False,
                                                          # xticks=x_ticks,
                                                          figsize=fig_size,
                                                          rangetool=True,
                                                          toolbar_location="above",
                                                          )
        plots.append(p_batteries)

        output_file("results.html")

        try:
            save(column(plots))
        except RuntimeError:
            print()
        print("Results are saved to results.html.")

# def organise_daily_results(df_dates, results):
#     num_batteries = len(results[b_discharges])
#
#     df = pd.DataFrame()
#     df[d_datetime] = df_dates
#     df[d_net_demand] = results[d_net_demand]
#     df[b_modified_demand] = results[b_modified_demand]
#     df[b_modified_max_demand] = [results[b_modified_max_demand]] * len(results[b_discharges][0])
#     for i, ch, dis in zip(range(num_batteries), results[b_charges], results[b_discharges]):
#         df[b_charges + str(i)] = ch
#         df[b_discharges + str(i)] = dis
#
#     return df
#
#
# def draw_daily_results(df):
#     x_ticks = [0] + [i for i in range(1, len(df)) if (i + 1) % 2 == 0]
#     df.to_csv("daily_results.csv")
#
#     p_demands = df.loc[:, [d_datetime, d_net_demand, b_modified_demand, b_modified_max_demand]] \
#         .plot_bokeh(kind="line", xlabel="Date time", ylabel="Demand (kW)",
#                     title="Demand (kW)",
#                     plot_data_points=True,
#                     x=d_datetime,
#                     show_figure=False,
#                     # xticks=x_ticks,
#                     figsize=(1600, 400),
#                     # rangetool=True,
#                     toolbar_location="above",
#                     )
#     df_batteries = df.drop(columns=[d_net_demand, b_modified_demand, b_modified_max_demand])
#     p_batteries = df_batteries.plot_bokeh(kind="line", xlabel="Date time", ylabel="Demand (kW)",
#                                           title="Battery activities (kW)",
#                                           plot_data_points=True,
#                                           x=d_datetime,
#                                           show_figure=False,
#                                           # xticks=x_ticks,
#                                           figsize=(1600, 400),
#                                           # rangetool=True,
#                                           toolbar_location="above",
#                                           )
#
#     # plots = [[p_demands], [p_batteries]]
#     output_file("results.html")
#
#     try:
#         save(column(p_demands, p_batteries))
#     except RuntimeError:
#         print()
#     print("Results are saved to results.html.")
