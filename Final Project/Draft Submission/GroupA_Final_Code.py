# -*- coding: utf-8 -*-
"""
Created on Wed May 10 15:48:05 2023

@author: Hannah
"""

# Import relevant libraries
import yahoo_fin.options as ops
import yahoo_fin.stock_info as si
import opstrat as op
import datetime as dt
import pandas as pd
from optionprice import Option
#from dateutil import parser
import streamlit as st
from datetime import datetime
st.set_option('deprecation.showPyplotGlobalUse', False)


# Get inputs from Streamlit fields
def getInputs():
    # input stock name 
    stock_str = st.text_input("Enter Stock\n>>>")
    try: stock = str(stock_str)
    except: stock = None    
    
    # Get expiry dates of stock options from input
    expirationDates = ops.get_expiration_dates(stock)
    expirationDatesdf = pd.DataFrame(expirationDates, columns=['Expiration Dates'])
    # User enter's option date of choice
    optionDate_str = st.selectbox(
        'Click a date from above that you\'d like to exercise an options trade(s)\n>>>',
         expirationDatesdf['Expiration Dates'])

    try: optionDate = datetime.strptime(optionDate_str, '%B %d, %Y').date()    # not sure about this part    
    except: optionDate = None
    
    # Enter price of stock at option expiry (strike price)
    strike_str = st.number_input('Enter a strike price in USD for your option(s)\n E.G.: 2.5\n>>>')
    try: strike = float(strike_str)
    except: strike = None
    
    # Get the nunber of contracts user wants to exercise
    num_option_str = st.number_input('Enter how many contracts you would like to exercise:\n>>>', format="%.0f")
    try: num_option = int(num_option_str)
    except: num_option = None
    
    # define which strategy to use 
    # how to turn into the function to use
    option_type_str = st.text_input('Click on the optimal strategy (call or put): \n>>>')
    try: option_type = str(option_type_str).lower()
    except: option_type = None
    
    return stock, optionDate, strike, num_option, option_type
    st.write(stock, optionDate, strike, num_option, option_type)
    
    
def stockInfo(stock):
    
    # Get today's date
    today = dt.date.today()
    todaysDate = today.strftime('%m/%d/%Y')

    # Define today_stock and set it to None
    today_stock = None

    # Get data from stock's most recent close
    try:
        daily = si.get_data(stock, start_date="01/01/2000", end_date=todaysDate, index_as_date = True, interval="1d") 
        st.line_chart(daily['adjclose'])
        today_stock = daily.iloc[-1]
    except:
        today_stock = None
    
    # Get stock's most recent price to use as Spot Price
    spot = today_stock[3] if today_stock is not None else None
    
    return todaysDate, spot


def getInterest(todaysDate, optionDate):
    
    if optionDate is None:
        return None, None
    # Format expiry date to mm/dd/yyyy
    #dateObj = parser.parse(optionDate)
    #formattedExpiryDate = dateObj.strftime("%m/%d/%Y")
    formattedExpiryDate = optionDate.strftime("%m/%d/%Y")
        
    #Difference in days between Expiry Date and Today's Date
    date_format = "%m/%d/%Y"
    date1 = dt.datetime.strptime(todaysDate, date_format)
    date2 = dt.datetime.strptime(formattedExpiryDate, date_format)

    # Calculate the difference
    timedelta = date2 - date1

    # Convert the difference to a number of days
    days = timedelta.days
    
    # ----------------------------------------------------------------------
    # want to get the interest rate close to the expiry date. Extract data from US treasury website
    url = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value=2023"
    dfs = pd.read_html(url)
    df = dfs[0]
    
    # Treasury Rate is given by a range of 1 Month to 10 Years.
    # This cell maps this range into days from months and years.  Rates are now represented by a number of days,
    # and the code below fits the closest bucket of days to the number of days until expiry to determine the most
    # appropriate rate to determine the option price

    ############## Start of Data Wrangling ####################
    exclude_start = 1
    exclude_end = 9

    selected_columns = df.iloc[:, [*range(exclude_start), *range(exclude_end + 1, df.shape[1])]]

    selected_columns.set_index('Date',inplace = True)
    treasuryRateChart = selected_columns.tail(1).transpose()

    newIndex = [30,60,90,120,180,365,365*2,365*3,365*5,365*7,365*10,365*20,365*30]

    treasuryRateChart.index = newIndex

    newColumnName = ['Rates']
    treasuryRateChart.columns = newColumnName
    treasuryRateChart.index.name = 'Days'

    ############### End of Data Wrangling ##################

    # Finds the best fit rate based on the number of days until expiry 
    closestIndex = min(treasuryRateChart.index, key=lambda x: abs(x - days))
    closestValue = treasuryRateChart.loc[closestIndex,'Rates']

    return days, closestValue 


def callOptionCalc(stock, optionDate, strike, spot, days, closestValue):
    
  
    # Get call options of stock for provided expiry date
    calls = ops.get_calls(stock,optionDate)
    calls.set_index("Contract Name",inplace = True)

    # Get data from call option based on expiry date and strike price
    call = calls[calls['Strike'] == strike]
    call = call.to_dict(orient='records')[0]
    
    #Get implied volatility from option
    percentage_float = float(call['Implied Volatility'].strip('%'))/100
    
    # == Code from https://sanketkarve.net/automating-option-pricing-calculations/ ==
    #Define option
    option_det = Option(european=True,
                        kind='call',
                        s0=spot,
                        k=strike,
                        t=days,
                        sigma=percentage_float,
                        r= (closestValue/100),
                        dv=0) 
    
    # Get option price
    optionPrice = option_det.getPrice(method='BSM',iteration=5000)
    # == end code from https://sanketkarve.net/automating-option-pricing-calculations/ ==
    
    return optionPrice


def putOptionCalc(stock, optionDate, strike, spot, days, closestValue):

    # Get put options of stock for provided expiry date
    puts = ops.get_puts(stock,optionDate)
    puts.set_index("Contract Name",inplace = True)
    
    # Get data from put option based on expiry date and strike price
    put = puts[puts['Strike'] == strike]
    put = put.to_dict(orient='records')[0]

    #Get implied volatility from option
    percentage_float = float(put['Implied Volatility'].strip('%'))/100

    # == Code from https://sanketkarve.net/automating-option-pricing-calculations/ ==
    # Define option and get option price 
    option_det = Option(european=True,
                        kind='put',
                        s0=spot,
                        k=strike,
                        t=days,
                        sigma=percentage_float,
                        r=closestValue/100,
                        dv=0)

    optionPrice = option_det.getPrice(method='BSM',iteration=5000)
    # == end code from https://sanketkarve.net/automating-option-pricing-calculations/ ==
     
     
    return optionPrice


def singleCallPayoffDiagram(spot, strike, num_option, optionPrice):
    
    if optionPrice is None:
        return None, None
    # == Code from https://sanketkarve.net/automating-option-pricing-calculations/ ==
    # Create dataframe that shows payoffs of option based on probable Equity Prices at Expiry
    #pct_change = int(Strike/10)
    ploss = {'Equity Market Price at Expiry': [spot*.7,spot*.8,spot*.9,
                                               spot,spot*1.1,spot*1.2,spot*1.3]}
    ## Ask for number of contracts
    sperc = 100*num_option #100 shares per contract
    # cpt = 10 + num_option # $10 flat/premium + $1 per contract (an option to add in the code for specific trading platform)
    df = pd.DataFrame(ploss, columns = ['Equity Market Price at Expiry','Profit/Loss for Long Call', 'Profit/Loss for Short Call'])
    payoffs_long = []
    payoffs_short = []
    for i in df['Equity Market Price at Expiry']:

    # Calculate Option Payoffs
            payoff_long = max(((i - strike) * sperc) - (optionPrice*sperc), -optionPrice*sperc)
            payoff_short = -1 * max(((i - strike) * sperc) - (optionPrice*sperc), -optionPrice*sperc)
            payoffs_long.append(payoff_long)
            payoffs_short.append(payoff_short)

    # Create DataFrame
    ploss['Profit/Loss for Long Call'] = payoffs_long
    ploss['Profit/Loss for Short Call'] = payoffs_short
    final=pd.DataFrame(ploss,columns=['Equity Market Price at Expiry','Profit/Loss for Long Call', 'Profit/Loss for Short Call']).set_index('Equity Market Price at Expiry')
    # == end code from https://sanketkarve.net/automating-option-pricing-calculations/ ==
    
    # Determine Long/short & call/put

    # Plot Option
    # For long call option
    fig1 = op.single_plotter(spot=spot, strike=strike, op_type='c', tr_type='b', op_pr=optionPrice,spot_range = 100)
    # For short call option
    fig2 = op.single_plotter(spot=spot, strike=strike, op_type='c', tr_type='s', op_pr=optionPrice,spot_range = 100)
    #st.pyplot(fig1)
    
    return final, fig1, fig2


def singlePutPayoffDiagram(spot, strike, num_option, optionPrice):
    
    if optionPrice is None:
        return None, None
    # == Code from https://sanketkarve.net/automating-option-pricing-calculations/ ==
    # Create dataframe that shows payoffs of option based on probable Equity Prices at Expiry
    #pct_change = int(Strike/10)
    ploss = {'Equity Market Price at Expiry': [spot*.7,spot*.8,spot*.9,
                                               spot,spot*1.1,spot*1.2,spot*1.3]}
    ## Ask for number of contracts
    sperc = 100*num_option #100 shares per contract
    # cpt = 10 + num_option # $10 flat/premium + $1 per contract (an option to add in the code for specific trading platform)
    df = pd.DataFrame(ploss, columns = ['Equity Market Price at Expiry','Profit/Loss for Long Put', 'Profit/Loss for Short Put'])
    payoffs_long = []
    payoffs_short = []
    for i in df['Equity Market Price at Expiry']:

    # Calculate Option Payoffs
            payoff_long = max(((strike - i) * sperc) - (optionPrice*sperc), -optionPrice*sperc)
            payoff_short = -1 * max(((strike - i) * sperc) - (optionPrice*sperc), -optionPrice*sperc)
            payoffs_long.append(payoff_long)
            payoffs_short.append(payoff_short)

    # Create DataFrame
    ploss['Profit/Loss for Long Put'] = payoffs_long
    ploss['Profit/Loss for Short Put'] = payoffs_short
    final=pd.DataFrame(ploss,columns=['Equity Market Price at Expiry','Profit/Loss for Long Put', 'Profit/Loss for Short Put']).set_index('Equity Market Price at Expiry')
    # == end code from https://sanketkarve.net/automating-option-pricing-calculations/ ==
     
    
    # Plot Option
    # For long call option
    fig1 = op.single_plotter(spot=spot, strike=strike, op_type='p', tr_type='b', op_pr=optionPrice, spot_range = 100)
    # For short call option
    fig2 = op.single_plotter(spot=spot, strike=strike, op_type='p', tr_type='s', op_pr=optionPrice, spot_range = 100)
    #st.pyplot(fig1)
    
    return final, fig1, fig2

# The code works but the combination of different types and prices is too complex 
# Would like to discuss more to modify the code. Below are the example for two options with the same position   
#def multiPayoffDiagram(spot, strike, optionPrice):
    
    # Plot Put and Call
    #op1={'op_type': 'p', 'strike': strike, 'tr_type': 'b', 'op_pr': pricePut}
    #op2={'op_type': 'c', 'strike': strike, 'tr_type': 'b', 'op_pr': priceCall}

    #op_list=[op1, op2]
    #fig3= op.multi_plotter(spot=spot, op_list=op_list,spot_range = 100)
    #st.pyplot(fig3)

# End of example
    
    
def displayResults(stock, optionDate, strike, num_option, final, fig1, fig2):
    if stock == None or optionDate == None or strike == None or num_option == None:
        return
    
    st.dataframe(final)
    st.pyplot(fig1)
    st.pyplot(fig2)


#------------------------------------------------------------------------------------------------------
st.title("Single Option Trading with Opstrat")
st.write("Welcome to the Option Trading application.")

# input parameters
stock, optionDate, strike, num_option, strategy = getInputs()
    
# calculate 
todaysDate, spot = stockInfo(stock)
days, closestValue = getInterest(todaysDate, optionDate)

# define new variable to avoid error on the webpage
optionPrice = None
final = None
fig1 = None
fig2 = None

if strategy == 'call':
    optionPrice = callOptionCalc(stock, optionDate, strike, spot, days, closestValue)
    final, fig1, fig2 = singleCallPayoffDiagram(spot, strike, num_option, optionPrice)
elif strategy == 'put':
    optionPrice = putOptionCalc(stock, optionDate, strike, spot, days, closestValue)
    final, fig1, fig2 = singlePutPayoffDiagram(spot, strike, num_option, optionPrice)
    

displayResults(stock, optionDate, strike, num_option, final, fig1, fig2)

    