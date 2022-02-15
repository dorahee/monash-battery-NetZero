class DemandCharge:

    def __init__(self):
        self.num_charges = 0
        self.demand_charges = dict()
        self.demand_charge_fields = [r_charge_name, r_peak_demand_charge, r_months, r_cycle_start_month,
                                     r_demand_threshold]
        for key in self.demand_charge_fields:
            self.demand_charges[key] = []

    def set_demand_charge_fields(self, fields):
        self.demand_charge_fields = fields

    def new(self, name, rate, months, cycle_start_month):
        self.demand_charges[r_charge_name].append(name)
        self.demand_charges[r_peak_demand_charge].append(rate)
        self.demand_charges[r_cycle_start_month].append(cycle_start_month)
        self.demand_charges[r_months].append(months)
        self.demand_charges[r_demand_threshold].append(0)
        self.num_charges += 1
        print(name, "is added.")

    def reset_demand_thresholds(self, current_time_step, next_time_step):

        next_month = next_time_step.month
        current_month = current_time_step.month

        if next_month != current_month:
            for i in range(self.num_charges):
                if (next_month == self.demand_charges[r_cycle_start_month][i]
                     or next_month not in self.demand_charges[r_months][i]):
                    # if self.demand_charges[r_demand_threshold][i] > 0:
                    self.demand_charges[r_demand_threshold][i] = 0
                    # print(f"{self.demand_charges[r_charge_name][i]} NA")
