# test FixedRateBond class - hard-coded inputs

from FixedRateBond import FixedRateBond
from datetime import date

principal = 1000
coupon = .05
frequency = 4
years = 3
maturity = date(2023, 6, 1)

bond = FixedRateBond(principal, coupon, frequency, years, maturity)

bond.printFlows()
