# User Guide

#### Purpose

This Python package is developed for managing the batteries to minimise the peak demand charges for Victories C&I customers. 
Instructions of running this algorithm on Mac are as the following: 

#### Installation Instructions

1.	Install MiniZinc IDE

The purpose of this step is to install the solver required for running the optimisation model. 
The instructions for installing the MiniZinc IDE are provided in the following website:

https://www.minizinc.org/software.html

2.	Prepare the Python environment

a)	Install PIP: https://phoenixnap.com/kb/install-pip-windows

b)	Install the required packages:

```pip3 install pandas minizinc numpy pandas-bokeh pathlib holidays```


#### Run the Program 

1. Call the operation function

```
opt = operation.Operation()
schedules_json, tracker_json, charges_json, result_status = \
                    opt.run(batteries_json=batteries_json, batteries_file_name=batteries_file_name,
                            charges_json=charges_json, charges_file_name=charges_file_name,
                            forecasts_json=forecasts_json, forecasts_file_name=forecasts_file_name,
                            actual_json=actual_json, actual_file_name=actual_file_name,
                            tracker_json=tracker_json, tracker_file_name=tracker_file_name,
                            schedule_json=schedule_json, schedule_file_name=schedule_file_name,
                            # thresholds_json=thresholds_json, thresholds_file_name=thresholds_file_name,
                            solver=solver, current_date_time=current_date_time,
                            data_folder=data_folder)
```

Details of the input and output data are provided in the Wiki. 