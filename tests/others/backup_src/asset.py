from src.monash_battery.param import *


# read battery specs in kW or kWh
class Battery:

    def __init__(self):
        self.specs = dict()
        self.num_batteries = 0
        self.aggregate_demand = []

    def new(self, init_cap, min_cap, max_cap, power, eff, name):
        self.specs[name] = dict()
        self.specs[name][b_init_energy] = init_cap
        self.specs[name][b_max_powers] = power
        self.specs[name][b_min_caps] = min_cap
        self.specs[name][b_max_caps] = max_cap
        self.specs[name][b_effs] = eff
        self.num_batteries = len(self.specs)

        print(name, "is added. ")

    def update_initial_capacities(self, solutions_tracker):
        for n in self.specs.keys():
            for col in solutions_tracker.all_schedules.columns.values:
                if n in col[0] and b_soc in col[1]:
                    self.specs[n][b_init_energy] = solutions_tracker.all_schedules[col].values[-1]
