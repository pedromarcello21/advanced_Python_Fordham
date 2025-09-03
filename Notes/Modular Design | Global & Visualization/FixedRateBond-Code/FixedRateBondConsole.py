# test FixedRateBond class - prompt for inputs

from FixedRateBond import FixedRateBond
from datetime import date

principal = 1000
coupon = float(input('Enter coupon (%): ')) / 100.0
frequency = int(input('Enter frequency (times/year): '))
years = int(input('Enter time to maturity (years): '))

maturity_s = input('Enter maturity date (mm/dd/yyyy): ')
m, d, y = maturity_s.split('/')
maturity = date(int(y), int(m), int(d))

bond = FixedRateBond(principal, coupon, frequency, years, maturity)

df = bond.cashflows()
print(df)
