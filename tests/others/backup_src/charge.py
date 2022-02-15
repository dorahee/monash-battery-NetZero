from src.monash_battery.param import *


class DemandCharge:

    def __init__(self):
        self.num_charges = 0
        self.demand_charges = dict()

    def new(self, name, rate, months, times):

        self.demand_charges[name] = dict()
        self.demand_charges[name][r_rate] = rate
        self.demand_charges[name][r_months] = months
        self.demand_charges[name][r_times] = times
        self.demand_charges[name][r_demand_threshold] = 0

        self.num_charges = len(self.demand_charges)
        print(name, "is added.")

    def update_thresholds(self, solutions_tracker):
        for n in self.demand_charges.keys():
            for col in solutions_tracker.all_thresholds.columns.values:
                if len(col) > 1 and n in col[0] and r_demand_threshold in col[1]:
                    self.demand_charges[n][r_demand_threshold] = solutions_tracker.all_thresholds[col].values[-1]
        print("Thresholds", [x[r_demand_threshold] for x in self.demand_charges.values()])

