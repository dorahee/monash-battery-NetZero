from src.monash_microgrid.common.param import *
import json, os


def input_parameters(folder):
    def write_to_json_file(data_folder, file_name, json_str, data_name):
        json_file = f"{data_folder}{file_name}"
        if os.path.exists(json_file):
            os.remove(json_file)
        if json_str is not None or json_str != "":
            with open(json_file, "w") as f:
                json.dump(json_str, f, indent=4)
            print(f"The {data_name} json is made. ")

    # create a json that contains battery information
    # note: the battery initial energy levels need to be refreshed according to the
    # actual data at the time of the optimisation
    batteries = dict()
    batteries["Li-on"] = dict()
    batteries["Li-on"][b_init_soc] = 134
    batteries["Li-on"][b_min_soc] = 0
    batteries["Li-on"][b_max_soc] = 134
    batteries["Li-on"][b_max_powers] = 120
    batteries["Li-on"][b_effs] = 0.88
    batteries["VFB"] = dict()
    batteries["VFB"][b_init_soc] = 900
    batteries["VFB"][b_min_soc] = 0
    batteries["VFB"][b_max_soc] = 900
    batteries["VFB"][b_max_powers] = 180
    batteries["VFB"][b_effs] = 0.65
    batteries_json = json.dumps(batteries)
    batteries_file_name = f"{f_battery}.json"
    write_to_json_file(folder, batteries_file_name, batteries_json, f_battery)

    # create a json that contains peak demand charges
    rates = dict()
    rates["trigger_price"] = dict()
    rates["trigger_price"][r_rate] = 200.0 * 1000  # dollar kwh
    rates["trigger_price"][d_unit] = d_kwh
    rates_json = json.dumps(rates)
    rates_file_name = f"{f_charge}.json"
    write_to_json_file(folder, rates_file_name, rates_json, f_charge)

    demand_forecast_json = ""
    demand_forecast_file_name = f"{f_demand_forecast}.json"
    write_to_json_file(folder, demand_forecast_file_name, None, f_demand_forecast)

    actual_demands_json = ""
    actual_demands_file_name = f"{f_actual_demand}.json"
    write_to_json_file(folder, actual_demands_file_name, None, f_actual_demand)

    price_forecast_json = ""
    price_forecast_file_name = f"{f_price_forecast}.json"
    write_to_json_file(folder, price_forecast_file_name, None, f_price_forecast)

    actual_prices_json = ""
    actual_prices_file_name = f"{f_actual_price}.json"
    write_to_json_file(folder, actual_prices_file_name, None, f_actual_price)

    schedule_json = ""
    schedule_file_name = f"{f_schedule}.json"
    write_to_json_file(folder, schedule_file_name, None, f_schedule)

    tracker_json = ""
    tracker_file_name = f"{f_tracker}.json"
    write_to_json_file(folder, tracker_file_name, None, f_tracker)

    thresholds_json = ""
    # thresholds_file_name = f"{f_threshold}.json"
    # write_to_json_file(folder, thresholds_file_name, None, f_threshold)

    solver = "gurobi"

    return batteries_json, batteries_file_name, \
           rates_json, rates_file_name, \
           demand_forecast_json, demand_forecast_file_name, \
           actual_demands_json, actual_demands_file_name, \
           price_forecast_json, price_forecast_file_name, \
           actual_prices_json, actual_prices_file_name, \
           schedule_json, schedule_file_name, \
           tracker_json, tracker_file_name, \
           solver
           # thresholds_json, thresholds_file_name, \
