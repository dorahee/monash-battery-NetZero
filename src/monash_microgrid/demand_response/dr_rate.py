from src.monash_microgrid.common.param import *
from src.monash_microgrid.data import dataIO


class DemandResponseRate(dataIO.DataIO):

    def __init__(self):
        super().__init__()
        self.trigger_price = 0

    def new(self, rate_name, rate):
        self.data_dict[rate_name] = dict()
        self.data_dict[rate_name][r_rate] = rate
        self.len_data = len(self.data_dict)

    def update_trigger_price(self):
        self.trigger_price = list(self.data_dict.values())[0][r_rate]

