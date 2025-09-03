#!/usr/bin/env python
# coding: utf-8

# In[4]:


# Import relevant libraries
import yahoo_fin.options as ops
import yahoo_fin.stock_info as si
import opstrat as op
import datetime as dt
import pandas as pd
from optionprice import Option
from dateutil import parser
import streamlit as st


# In[5]:


st.title("Option Trading with Opstrat")
st.write("Welcome to the Option Trading application.")


# In[6]:


# Get today's date
today = dt.date.today()
todaysDate = today.strftime('%m/%d/%Y')

# User enters stock for options trading
stock = st.text_input("Enter Stock\n>>>")


# In[7]:


# Get expiry dates of stock options from input
expirationDates = ops.get_expiration_dates(stock)
expirationDatesdf = pd.DataFrame(expirationDates, columns=['Expiration Dates'])
#st.dataframe(expirationDatesdf)


# In[8]:


# User enter's option date of choice
#optionDate = st.text_input('Enter a date from above that you\'d like to exercise an options trade(s)\n>>>')
optionDate = st.selectbox(
    'Click a date from above that you\'d like to exercise an options trade(s)\n>>>',
     expirationDatesdf['Expiration Dates'])
st.write('You selected: ', optionDate)


# In[9]:




