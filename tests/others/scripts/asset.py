from scripts.param import *


# read battery specs in kW or kWh
class Battery:

    def __init__(self):
        self.specs = dict()
        self.num_batteries = 0
        self.specs_fields = [name, b_init_energy, b_max_powers, b_min_caps, b_max_caps,
                             b_effs]
        for key in self.specs_fields:
            self.specs[key] = []

    def new(self, init_cap, min_cap, max_cap, power, eff, name):
        self.specs[name].append(name)
        self.specs[b_init_energy].append(init_cap)
        self.specs[b_min_caps].append(min_cap)
        self.specs[b_max_caps].append(max_cap)
        self.specs[b_max_powers].append(power)
        self.specs[b_effs].append(eff)
        self.num_batteries += 1
        print(name, "is added. ")

    def update_init_energy_levels(self, optimiser, start_time):
        results = optimiser.solution_df

        if not results.empty:
            self.specs[b_init_energy] = []
            if start_time > results.index[-1]:
                for i in self.specs[name]:
                    self.specs[b_init_energy].append(results[i + ": " + b_soc][-1])
            else:
                for i in self.specs[name]:
                    self.specs[b_init_energy].append(results[i + ": " + b_soc][:start_time][-1])
