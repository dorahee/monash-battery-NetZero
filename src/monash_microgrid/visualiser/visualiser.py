from src.monash_microgrid.common.param import *
from src.monash_microgrid.data import dataIO
from pandas_bokeh import *
from pathlib import Path
from bokeh.models import LinearAxis, Range1d, HoverTool, ColumnDataSource, RangeTool
from bokeh.plotting import figure, show, output_file
from bokeh.palettes import Spectral4, Set3, Set2, Pastel1, Spectral


class Visualiser(dataIO.DataIO):

    def __init__(self, ):
        super().__init__()
        self.exp_datetime = ""
        self.output_folder = ""

    def add_results(self, tracker):
        self.data_dict = tracker.data_dict

        # convert the dictionary to a pandas data frame
        self.dict_to_dataframe()

        # calculate the len of the data
        self.len_data = len(self.data_dict)

    def write(self, output_folder, file_name, note):

        # self.exp_datetime = datetime.now().strftime("%b-%d_%H-%M-%S")
        if not output_folder.endswith('/'):
            output_folder += "/"
        self.output_folder = output_folder
        Path(output_folder).mkdir(parents=True, exist_ok=True)

        self.__save_to_csv(file_name)
        self.__save_to_graphs(file_name, note)

    def __save_to_csv(self, file_name):

        self.data_df.to_csv(f"{self.output_folder}{file_name}.csv")

    def __save_to_graphs(self, file_name, note):

        # common setting for all graphs
        source = ColumnDataSource(self.data_df)
        tools = ["xpan", "xwheel_zoom", "reset"]
        tooltips = [("Date time:", f"@{d_datetime}{{%F %H:%M}}")]
        plot_height = 400

        # divide the columns into three sets
        columns_demands = []
        columns_batteries = [b_agg_demands]
        columns_prices = []

        for col in self.data_df.columns:
            if "threshold" in col or "demand" in col:
                columns_demands.append(col)
            elif ("charge" in col or "discharge" in col or "soc" in col) and \
                    "threshold" not in col:
                columns_batteries.append(col)
            elif "price" in col:
                columns_prices.append(col)

        # ---------- demand graphs ----------
        max_demand = self.data_df[columns_demands].max().values.max() * 1.1
        min_demand = min(0, self.data_df[columns_demands].min().values.min() * 1.1)

        p_demands_prices = figure(title="Demand (kW) " + note,
                                  x_axis_label="Date time", x_axis_type="datetime",
                                  y_axis_label="Demand (kW)", y_range=(min_demand, max_demand),
                                  height=plot_height, sizing_mode="stretch_both",
                                  tools=tools, toolbar_location="above",
                                  active_scroll="xwheel_zoom")

        tooltips_demands_prices = tooltips
        tooltips_demands_prices_graphs = []

        for col, color in zip(columns_demands, Spectral[6]):
            tooltips_demands_prices.append((col, f"@{{{col}}}{{0, 0.00}}"))
            line_graph = p_demands_prices.line(x=d_datetime, y=col, legend_label=col, line_width=2, source=source,
                                               muted_alpha=0.2, color=color, muted_color=color)
            # p_demands_prices.circle(x=d_datetime, y=col, size=5,
            #                         fill_color=color, fill_alpha=0,
            #                         hover_fill_color=color, hover_alpha=0.3,
            #                         line_color=None, hover_line_color="white", source=source)
            if "actual" in col:
                tooltips_demands_prices_graphs = [line_graph]

        # ---------- price graphs ----------
        if len(columns_prices) > 0:
            max_price = self.data_df[columns_prices].max().values.max() * 1.1
            min_price = min(0, self.data_df[columns_prices].min().values.min() * 1.1)
            extra_y_axis_name = "Price ($/kWh)"
            p_demands_prices.extra_y_ranges = {extra_y_axis_name: Range1d(start=min_price, end=max_price)}

            for col, color in zip(columns_prices, Pastel1[6]):
                tooltips_demands_prices.append((col, f"@{{{col}}}{{0, 0.00}}"))
                p_demands_prices.line(x=d_datetime, y=col, legend_label=col, line_width=2,
                                      muted_alpha=0.2, color=color, muted_color=color,
                                      y_range_name=extra_y_axis_name, source=source)
            p_demands_prices.add_layout(LinearAxis(y_range_name=extra_y_axis_name, axis_label="Price ($)"), "right")

        hover_tool = HoverTool(renderers=tooltips_demands_prices_graphs, tooltips=tooltips_demands_prices, mode="vline")
        hover_tool.formatters = {f"@{d_datetime}": "datetime"}
        p_demands_prices.add_tools(hover_tool)
        p_demands_prices.legend.click_policy = "mute"

        # ---------- battery graphs ----------
        p_batteries1 = figure(title="Demand (kW)",
                              x_range=p_demands_prices.x_range, x_axis_label="Date time", x_axis_type="datetime",
                              y_axis_label="Demand (kW)",
                              height=plot_height, sizing_mode="stretch_both",
                              tools=tools, toolbar_location="above", active_scroll="xwheel_zoom")

        tooltips_batteries = tooltips
        tooltips_batteries_graphs = []

        for col, color in zip(columns_batteries, Spectral[10]):
            tooltips_batteries.append((col, f"@{{{col}}}{{0, 0.00}}"))
            line_graph = p_batteries1.line(x=d_datetime, y=col, legend_label=col, line_width=2, source=source,
                                           muted_alpha=0.2, color=color, muted_color=color)
            # p_batteries1.circle(x=d_datetime, y=col, size=5,
            #                     fill_color=color, fill_alpha=0,
            #                     hover_fill_color=color, hover_alpha=0.3,
            #                     line_color=None, hover_line_color="white", source=source)

            if "agg" in col:
                tooltips_batteries_graphs = [line_graph]

        
        # ---------- hover tooltips ----------
        hover_tool = HoverTool(renderers=tooltips_batteries_graphs, tooltips=tooltips_batteries, mode="vline")
        hover_tool.formatters = {f"@{d_datetime}": "datetime"}
        p_batteries1.add_tools(hover_tool)
        p_batteries1.legend.click_policy = "mute"

        # ---------- save graphs ----------
        plots = [p_demands_prices, p_batteries1]
        output_file(f"{self.output_folder}/{file_name}.html")
        layout1 = column(plots)
        layout1.sizing_mode = "stretch_both"
        save(layout1)
        # print(f"Results are saved to {file_name}.html.")

# # ---------- previous code ----------
#         self.combined = self.data_df.loc[:, columns_demands]
#         self.schedules_history = self.data_df.loc[:, columns_batteries]
#         if len(columns_prices) > 0:
#             self.combined = self.data_df.loc[:, columns_demands].join(self.data_df.loc[:, columns_prices])
#
#         # draw each graph
#         fig_size = (1500, 300)
#         p_demands = self.combined \
#             .plot_bokeh(kind="line", xlabel="Date time",
#                         ylabel="Demand (kW)",
#                         title="Demand (kW)",
#                         # plot_data_points=True,
#                         # x=d_datetime,
#                         y=columns_demands,
#                         show_figure=False,
#                         # xticks=x_ticks,
#                         figsize=fig_size,
#                         rangetool=True,
#                         toolbar_location="above",
#                         sizing_mode="stretch_width"
#                         )
#         if len(columns_prices) > 0:
#
#             p_demands.children[0].extra_y_ranges = {extra_y_axis_name: Range1d(start=min_price, end=max_price)}
#             p_demands.children[0].add_layout(LinearAxis(y_range_name=extra_y_axis_name, axis_label="Price ($)"),
#                                              "right")
#
#             for col in columns_prices:
#                 p_demands.children[0].line(x=self.combined.index,
#                                            y=self.combined[col],
#                                            y_range_name=extra_y_axis_name,
#                                            color="grey",
#                                            legend_label=col,
#                                            line_width=2)
#
#             p_demands.children[0].y_range.end = max_demand
#             p_demands.children[0].y_range.start = min_demand
#
#         p_batteries = self.schedules_history \
#             .plot_bokeh(kind="line", xlabel="Date time",
#                         ylabel="Demand (kW)",
#                         title="Battery activities (kW)",
#                         # plot_data_points=True,
#                         # x=d_datetime,
#                         show_figure=False,
#                         # xticks=x_ticks,
#                         figsize=fig_size,
#                         rangetool=True,
#                         toolbar_location="above",
#                         sizing_mode="stretch_width"
#                         )
#
#         # link xranges of graphs
#         p_batteries.children[0].x_range = p_demands.children[0].x_range
#         p_batteries.children[1].tools[0].x_range = p_demands.children[1].tools[0].x_range
#
#         def set_tooltips(dataframe, plot, keyword):
#             tooltips = [(d_datetime, "@__x__values_original{%F %T}")]
#             for col in dataframe.columns.values:
#                 v = (col, f"@{{{col}}}{{0, 0.00}}")
#                 if d_datetime not in col:
#                     tooltips.append(v)
#             plot.children[0].add_tools(HoverTool(tooltips=tooltips, mode='vline'))
#
#             for hover_tool in plot.children[0].hover:
#                 if keyword in hover_tool.tooltips[1][0]:
#                     hover_tool.tooltips = tooltips
#                 else:
#                     hover_tool.tooltips = None
#
#             # for render in plot._property_values['children'][0]._property_values['renderers']:
#             #     render.muted = True
#
#         set_tooltips(self.combined, p_demands, "actual")
#         set_tooltips(self.schedules_history, p_batteries, "discharge")
