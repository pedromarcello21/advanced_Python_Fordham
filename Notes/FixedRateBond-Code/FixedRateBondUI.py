# User interface for FixedRateBond using Streamlit

from FixedRateBond import FixedRateBond
from datetime import date
import streamlit as st

# Get inputs from Streamlit fields
def getInputs():
   years_str = st.text_input('Number of years:', key='years_input_field')
   try:    years = int(years_str)
   except: years = None

   coupon_str = st.text_input("Coupon rate (%): ", key='coupon_input_field')
   try:    coupon = float(coupon_str) / 100.0
   except: coupon = None

   frequency_str = st.text_input('Frequency: ', key='frequency_input_field')
   try:    frequency = int(frequency_str)
   except: frequency = None

   maturity_str = st.text_input('Maturity date: (mm/dd/yyyy)', key='maturity_input_field')
   try:
      month_str, day_str, year_str = maturity_str.split('/')
      month = int(month_str)
      day = int(day_str)
      year = int(year_str)
      maturity = date(year, month, day)
   except:
      maturity = None

   return years, coupon, frequency, maturity

   st.write(years, coupon, frequency, maturity)

# Display the cashflow schedule table and its bar chart
def displayResults(years, coupon, frequency, maturity):
   # if any inputs are None, the short-circuit return (no result display)
   if years == None or coupon == None or frequency == None or maturity == None:
       return

   principal = 1000.0
   bond = FixedRateBond(principal, coupon, frequency, years, maturity)

   df = bond.cashflows() # generate the cashflows
   df # display the DataFrame
   df.set_index(['Date'],inplace=True)
   st.bar_chart(df) # display the dataFrame as a bar chart

st.header('Fixed Rate Bond Cashflow Generator')

# INPUT: Get inputs
years, coupon, frequency, maturity = getInputs()

# For debugging - show inputs
st.write(years, coupon, frequency, maturity)

# OUTPUT: Call the displayResults() function
displayResults(years, coupon, frequency, maturity)