from src.monash_microgrid.peak_demand_management import pdm_stream


def main(forecasts_json, forecasts_file_name,
         actual_json, actual_file_name,
         batteries_json, batteries_file_name,
         charges_json, charges_file_name,
         schedule_json, schedule_file_name,
         tracker_json, tracker_file_name,
         solver, current_date_time, data_folder):

    # -------------------- All Ayesha needs: start -------------------- #
    opt = pdm_stream.PDMStream()
    schedules_json, tracker_json, charges_json, result_status = \
        opt.run(batteries_json=batteries_json, batteries_file_name=batteries_file_name,
                charges_json=charges_json, charges_file_name=charges_file_name,
                forecasts_json=forecasts_json, forecasts_file_name=forecasts_file_name,
                actual_json=actual_json, actual_file_name=actual_file_name,
                tracker_json=tracker_json, tracker_file_name=tracker_file_name,
                schedule_json=schedule_json, schedule_file_name=schedule_file_name,
                # thresholds_json=thresholds_json, thresholds_file_name=thresholds_file_name,
                solver=solver, observation_time=current_date_time,
                data_folder=data_folder)

    # -------------------- All Ayesha needs: end -------------------- #
