from src.monash_battery.param import *
from src.monash_battery import tracker
from pandas_bokeh import *
from datetime import datetime
from pathlib import Path


class Visualiser:

    def __init__(self):
        self.solutions_tracker = tracker.Tracker()
        self.exp_datetime = datetime.now().strftime("%b-%d_%H-%M-%S")
        Path("results").mkdir(parents=True, exist_ok=True)

    def add_inputs(self, solutions_tracker):
        self.solutions_tracker = solutions_tracker

    def save_to_csv(self):
        self.solutions_tracker.all_schedules.to_csv(f"results/{self.exp_datetime} - entire_schedules.csv")

    def save_to_graphs(self):
        self.solutions_tracker.consolidate()
        # self.solutions_tracker.all_demands = pd.merge(self.solutions_tracker.all_demands,
        #                                               self.solutions_tracker.all_thresholds, on=d_datetime)
        # for col in self.solutions_tracker.all_thresholds.columns.values:
        #     if d_datetime not in col:
        #         self.solutions_tracker.all_demands[col] = self.solutions_tracker.all_thresholds[col]

        self.solutions_tracker.all_demands.columns \
            = [' '.join(col).strip() if type(col) is tuple else col for col
               in self.solutions_tracker.all_demands.columns.values]

        self.solutions_tracker.all_schedules.columns \
            = [' '.join(col).strip() if type(col) is tuple else col for col
               in self.solutions_tracker.all_schedules.columns.values]

        fig_size = (1800, 300)
        p_demands = self.solutions_tracker.all_demands \
            .plot_bokeh(kind="line", xlabel="Date time",
                        ylabel="Demand (kW)",
                        title="Demand (kW)",
                        # plot_data_points=True,
                        x=d_datetime,
                        show_figure=False,
                        # xticks=x_ticks,
                        figsize=fig_size,
                        rangetool=True,
                        toolbar_location="above",
                        )

        p_batteries = self.solutions_tracker.all_schedules \
            .plot_bokeh(kind="line", xlabel="Date time",
                        ylabel="Demand (kW)",
                        title="Battery activities (kW)",
                        # plot_data_points=True,
                        x=d_datetime,
                        show_figure=False,
                        # xticks=x_ticks,
                        figsize=fig_size,
                        rangetool=True,
                        toolbar_location="above",
                        )

        # link xranges of graphs
        p_batteries._property_values['children'][0]._property_values['x_range'] \
            = p_demands._property_values['children'][0]._property_values['x_range']
        p_batteries._property_values['children'][1].tools[0]._property_values['x_range'] \
            = p_demands._property_values['children'][1].tools[0]._property_values['x_range']

        def set_tooltips(dataframe, plot, keyword):
            tooltips = [(d_datetime, "@__x__values_original{%F %T}")]
            for col in dataframe.columns.values:
                if d_datetime not in col:
                    tooltips.append((col, f"@{{{col}}}{{0,0.00}}"))
                # else:
                #     tooltips.append((col, "@__x__values_original{%F %T}"))

            for hover_tool in plot._property_values['children'][0].hover:
                if keyword in hover_tool._property_values['tooltips'][1][0]:
                    hover_tool._property_values['tooltips'] = tooltips
                    # hover_tool._property_values['formatters'] = {f'@{d_datetime}': 'datetime'}
                else:
                    hover_tool._property_values['tooltips'] = None

            # for render in plot._property_values['children'][0]._property_values['renderers']:
            #     render.muted = True

        set_tooltips(self.solutions_tracker.all_demands, p_demands, "threshold")
        set_tooltips(self.solutions_tracker.all_schedules, p_batteries, "discharge")

        p_demands.sizing_mode = "stretch_both"
        p_batteries.sizing_mode = "stretch_both"
        plots = [p_demands, p_batteries]
        output_file(f"results/{self.exp_datetime} - results.html")
        save(column(plots))
        print(f"Results are saved to {self.exp_datetime} - results.html.")
