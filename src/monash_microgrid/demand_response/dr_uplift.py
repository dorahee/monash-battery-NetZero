from src.monash_microgrid.data import dataIO


class TmaxUplift(dataIO.DataIO):

    def __init__(self):
        super().__init__()
        self.data_dict = {
            27: 1.06,
            28: 1.06,
            29: 1.06,
            30: 1.16,
            31: 1.16,
            32: 1.16,
            33: 1.16,
            34: 1.22,
            35: 1.22,
            36: 1.22,
            37: 1.22,
            38: 1.27,
            39: 1.27,
            40: 1.27,
        }

    def add_uplift_factor(self, temp, factor):
        if temp in self.data_dict:
            print("This temperature has an uplift factor associated with it. "
                  "Please use the update_lift_factor function to overwrite the existing factor. ")
        else:
            self.data_dict[temp] = factor

    def update_uplift_factor(self, temp, factor):
        self.data_dict[temp] = factor

    def read_uplift_factor(self, temp):
        all_temps = self.data_dict.keys()
        if temp < min(all_temps):
            factor = 1
        elif temp > max(all_temps):
            factor = self.data_dict[max(all_temps)]
        else:
            factor = self.data_dict[temp]
        return factor
