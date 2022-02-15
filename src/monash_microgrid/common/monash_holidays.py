from holidays import Australia

from datetime import date

from dateutil.easter import easter
from dateutil.relativedelta import relativedelta as rd, MO, SA, FR, WE, TU
from holidays.constants import JAN, MAR, APR, MAY, JUN, AUG, SEP, OCT, NOV, DEC
from holidays.constants import SAT, SUN, WEEKEND


def verify_non_work_days():

    monash_holidays_closedown = MonashNonWorkdays(state="VIC", prov="VIC")
    print(monash_holidays_closedown.get('2021-01-01'))
    print(monash_holidays_closedown.get('2021-01-02'))
    print(monash_holidays_closedown.get('2021-01-26'))
    print(monash_holidays_closedown.get('2021-04-02'))
    print(monash_holidays_closedown.get('2021-04-03'))
    print(monash_holidays_closedown.get('2021-04-04'))
    print(monash_holidays_closedown.get('2021-04-05'))
    print(monash_holidays_closedown.get('2021-04-06'))  # not working
    print(monash_holidays_closedown.get('2021-04-25'))
    print(monash_holidays_closedown.get('2021-09-24'))
    print(monash_holidays_closedown.get('2021-11-02'))
    print(monash_holidays_closedown.get('2021-12-23'))  # not working
    print(monash_holidays_closedown.get('2021-12-24'))  # not working
    print(monash_holidays_closedown.get('2021-12-25'))
    print(monash_holidays_closedown.get('2021-12-26'))  # not working
    print(monash_holidays_closedown.get('2021-12-27'))  # not working
    print(monash_holidays_closedown.get('2021-12-28'))  # not working
    print(monash_holidays_closedown.get('2021-12-29'))  # not working
    print(monash_holidays_closedown.get('2021-12-30'))  # not working
    print(monash_holidays_closedown.get('2021-12-31'))  # not working
    print(monash_holidays_closedown.get('2022-01-01'))
    print(monash_holidays_closedown.get('2022-01-02'))
    print(monash_holidays_closedown.get('2022-01-03'))


def check_workday(year, month, day):
    date_to_check = date(year, month, day)
    monash_holidays_closedown = MonashNonWorkdays()
    workday_status = True
    if date_to_check in monash_holidays_closedown:
        workday_status = False
    elif date_to_check.weekday() in WEEKEND:
        workday_status = False

    return workday_status


class MonashNonWorkdays(Australia):

    def __init__(self, **kwargs):
        Australia.__init__(self, **kwargs)

    def _populate(self, year):
        Australia._populate(self, year=year)

        # Easter Tuesday
        self[easter(year) + rd(weekday=TU)] = "Easter Tuesday"

        # Monash close down days
        closedown_days = [23, 24, 27, 28, 29, 30, 31]
        for d in closedown_days:
            d_date = date(year, DEC, d)
            if d_date not in self:
                self[d_date] = "University closedown"

        # remove non Monash holidays
        non_monash_holidays = ["Queen's Birthday", "Melbourne Cup", "Labour Day"]
        for d_name in non_monash_holidays:
            if d_name in self.values():
                self.pop_named(d_name)




