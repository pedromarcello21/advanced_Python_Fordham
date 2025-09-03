from datetime import date
from dateutil.relativedelta import relativedelta
import pandas as pd

# cashflow generator class for a fixed rate bond
class FixedRateBond:
    def __init__(self, principal, coupon, freq, years, maturityDate):
        self.principal = principal
        self.coupon = coupon # coupon rate in decimal
        self.freq = freq # frequency in payments per year
        self.years = years # life of bond in years
        self.maturityDate = maturityDate # maturity date of bond
    
    # string representation of bond
    def __str__(self):
        return str(self.principal)+','+str(self.coupon)+','+\
               str(self.freq)+','+\
               str(self.years)+','+str(self.maturityDate)
    
    # repr() for a bond
    __repr__ = __str__
    
    # generate cashflows
    def genFlows(self):
        dates = []
        for i in range(self.years*self.freq):
            delta = relativedelta(months=-12/self.freq*i)
            d = self.maturityDate + delta
            dates.insert(0, d)
        interestFlows = [self.principal*self.coupon/self.freq]*(self.years*self.freq)
        principalFlows = [0]*(self.years*self.freq)
        principalFlows[-1] = self.principal
        return dates, interestFlows, principalFlows
        
    # display cashflows
    def printFlows(self):
        dates, interestFlows, principalFlows = self.genFlows()
        print('dates:', dates)
        print('interest:', interestFlows)
        print('principal:', principalFlows)
    
    # return cashflows as a DataFrame
    def cashflows(self):
        dates, interestFlows, principalFlows = self.genFlows()
        df = pd.DataFrame({"Date": dates,
                           "Interest": interestFlows,
                           "Principal": principalFlows})
        return df