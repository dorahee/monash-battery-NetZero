import json, sys, pandas as pd
from pathlib import Path
from src.monash_microgrid.common.param import *


class DataIO:

    def __init__(self):
        # dict means the data is a dictionary
        self.data_dict = dict()

        # df means the data is a pandas data frame
        self.data_df = pd.DataFrame()

        # the len the of the data
        self.len_data = 0

    def read(self, json_str, folder, file_name):
        try:
            if json_str is not None and json_str != "":
                self.json_to_dict(json_str)
            else:
                self.json_file_to_dict(folder=folder, file_name=file_name)
            return True
        except:
            # print(f"Warning: the {file_name} is not read or not found. ")
            # print("Unexpected error:", sys.exc_info())
            return False

    def json_to_dict(self, json_str):
        # read the data from the json string into a dictionary
        self.data_dict = json.loads(json_str)

        # convert the dictionary to a pandas data frame
        self.dict_to_dataframe()

        # calculate the len of the data
        self.len_data = len(self.data_dict)

    def json_file_to_dict(self, folder, file_name):
        if not folder.endswith('/'):
            folder += "/"
        if not file_name.endswith(".json"):
            file_name += ".json"
        # read the json string from the file
        json_str = json.load(open(f"{folder}{file_name}"))
        self.json_to_dict(json_str)

    def dict_to_dataframe(self):
        # convert the dictionary to a pandas data frame
        self.data_df = pd.DataFrame.from_dict(self.data_dict)
        if d_datetime in self.data_df:
            self.data_df[d_datetime] = pd.to_datetime(self.data_df[d_datetime])
            self.data_df = self.data_df.set_index(d_datetime)

    def dict_to_json_str(self):
        # check if date time is in the dictionary data
        data_dict = self.data_dict
        if d_datetime in self.data_dict:
            if type(data_dict[d_datetime]) == list:
                data_dict[d_datetime] = [x.strftime('%Y-%m-%d %H:%M') if type(x) is not str else x
                                         for x in data_dict[d_datetime]]
            else:
                data_dict[d_datetime][d_value] = [x.strftime('%Y-%m-%d %H:%M') if type(x) is not str else x
                                                  for x in data_dict[d_datetime][d_value]]

        # convert the dictionary data into a json string
        json_str = json.dumps(data_dict)

        return json_str

    def dict_to_json_file(self, folder, file_name):
        json_str = self.dict_to_json_str()

        # create the folder if it does not exist yet
        if not folder.endswith('/'):
            folder += "/"
        Path(folder).mkdir(parents=True, exist_ok=True)

        if not file_name.endswith(".json"):
            file_name += ".json"

        # write the json string to the file
        with open(f"{folder}{file_name}", "w") as f:
            json.dump(json_str, f, indent=4)

        return json_str

