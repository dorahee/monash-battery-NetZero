from src.monash_microgrid.common.param import *
import json, os


def input_parameters(folder):
    # Path(folder).mkdir(parents=True, exist_ok=True)

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
    charges = dict()
    charges["annual_charge"] = dict()
    charges["annual_charge"][r_rate] = 131.7 * 1000
    charges["annual_charge"][r_months] = [i for i in range(1, 13)]
    charges["annual_charge"][r_times] = [x for x in range(7, 20)]
    charges["annual_charge"][r_demand_threshold] = 0
    charges["summer_charge"] = dict()
    charges["summer_charge"][r_rate] = 162.5 * 1000
    charges["summer_charge"][r_months] = [11, 12, 1, 2, 3]
    charges["summer_charge"][r_times] = [15, 16, 17, 18]
    charges["summer_charge"][r_demand_threshold] = 0
    charges_json = json.dumps(charges)
    charges_file_name = f"{f_charge}.json"
    write_to_json_file(folder, charges_file_name, charges_json, f_charge)

    forecast_json = ""
    forecast_file_name = f"{f_demand_forecast}.json"
    write_to_json_file(folder, forecast_file_name, None, f_demand_forecast)

    actual_json = ""
    actual_file_name = f"{f_actual_demand}.json"
    write_to_json_file(folder, actual_file_name, None, f_actual_demand)

    schedule_json = ""
    schedule_file_name = f"{f_schedule}.json"
    write_to_json_file(folder, schedule_file_name, None, f_schedule)

    tracker_json = ""
    tracker_file_name = f"{f_tracker}.json"
    write_to_json_file(folder, tracker_file_name, None, f_tracker)

    thresholds_json = ""
    # thresholds_file_name = f"{f_threshold}.json"
    # write_to_json_file(folder, thresholds_file_name, None, f_threshold)

    solver = "mip"

    return batteries_json, batteries_file_name, \
           charges_json, charges_file_name, \
           forecast_json, forecast_file_name, \
           actual_json, actual_file_name, \
           schedule_json, schedule_file_name, \
           tracker_json, tracker_file_name, \
           solver
           # thresholds_json, thresholds_file_name, \
