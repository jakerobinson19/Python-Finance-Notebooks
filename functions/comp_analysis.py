#!/usr/bin/env python
# coding: utf-8

# ## Industry Comparable Analysis using FinViz Financial Data
# 
# Comparable company analysis (or “comps” for short) is a valuation methodology that looks 
# at financials of similar public companies and uses them to derive the value of another business. 
# As a relative form of valuation, this analysis evaluates a company relative to its industry peers 
# using financial ratios such as Price-to-Earnings (P/E) or Price-to-Book (P/B), as well as debt and 
# profitability measures. 
# 
# Financial data is pulled from finviz.com using python requests and parsed using pd.read_html.
# 
# ## Built With
#  * Python 3
# 
# ## Written by: Jake Robinson (https://github.com/jakerobinson19)

# import pandas and requests packages
import pandas as pd
import requests

# iPython display packages for hiding underlying code
from IPython.display import HTML
from IPython.display import display

# Plotly visualization packages
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# global variables (mainly used for standardized url requests)
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
url = 'https://finviz.com/quote.ashx?t={}'.format(ticker)
combined_data = []

# METHODS 
# All methods here are available in the comp_analysis_functions.py file in the git repo)
# https://github.com/jakerobinson19/Python-Finance-Notebooks

# Extract the table data from finviz and convert into a pd dataframe
def extract_data_table(ind, code, page, headers=headers):
    
    url = 'https://finviz.com/screener.ashx?v={}&f=ind_{}&r={}1'.format(code,ind,page*2-2)
    html_response = requests.get(url, headers=headers).content

    dfs = pd.read_html(html_response)
    
    pages = dfs[13][3].str.split('/')[0][-1]
    
    data_table = dfs[14]
    headers = data_table.iloc[0]
    data_table = pd.DataFrame(data_table.values[1:], columns=headers).set_index('No.')
    
    return(data_table, int(pages))

# Intake a dataframe of companies to sort into small, mid, or large cap
def assign_cap_groupings(comp_data):
    caps = {'Small Cap': [],
        'Mid Cap': [],
        'Large Cap': []}

    for ticker in comp_data.index:
        mcap = str(comp_data.loc[ticker]['Market Cap'])

        if mcap != 'nan':
            mcap = [int(re.split('(\d+)',mcap)[1]), re.split('(\d+)',mcap)[-1]]
        else:
            continue
            
        if mcap[1] == 'M':
            caps['Small Cap'].append(ticker)
        elif mcap[0] < 10:
            caps['Mid Cap'].append(ticker)
        else:
            caps['Large Cap'].append(ticker)
        
    return(caps)

# Pull a specific tickers data by going to the corresponding finviz page and extracting into pd dataframe
def get_ticker_data(ticker):
    url = 'https://finviz.com/quote.ashx?t={}'.format(ticker)

    response = requests.get(url).content
    ticker_dfs = pd.read_html(response)

    ticker_financials = ticker_dfs[6]

    sector, industry, country = ticker_dfs[5][0][2].split('|')
    ind = format_string(industry)

    return(ticker_financials, ind)

# Using the industry, grab all companies from the finviz industry page and concat into one dataframe
def get_comp_data(ind, headers=headers):
    pg = 1
    
    val_data, pages = extract_data_table(ind, '121', pg)
    fin_data, pages = extract_data_table(ind, '161', pg)
    
    while pg < pages:
        pg += 1
        val_data = pd.concat([val_data, extract_data_table(ind, '121', pg)[0]])
        fin_data = pd.concat([fin_data, extract_data_table(ind, '161', pg)[0]])
    
    comp_data = pd.concat([val_data, fin_data],axis=1)
    comp_data = comp_data.T.drop_duplicates().T
    comp_data.set_index('Ticker',inplace=True)
    comp_data = comp_data.drop(['Earnings','Volume'],axis=1)

    return(comp_data)

# Calculate the industry averages for each financial measurement in the comparable data table
def get_industry_averages(comp_data):
    averages = None

    for column in comp_data:
        try:
            avg = comp_data[column].sum()/len(comp_data)
        except:
            continue
        
        avg = pd.DataFrame([[column,avg]], columns=['Type','Avg'])
    
        if averages is None:
            averages = avg
        else:
            averages = pd.concat([averages, avg])

    return(averages)

# Determine the instances where the ticker in question is better than the industry average
# Store each measurement where the ticker "beats" its competitors and tally up the total
def calculate_beats(tick_data, averages):
    beat_number = 0
    finrat_beats = []
    dbt_beats = []
    marg_beats = []
    
    for ind, value in enumerate(tick_data): 
        #print(ind,value,averages.iloc[ind]['Type'], float(averages.iloc[ind]['Avg']))
        if ind >= 0 and ind < 7:
            if value != 0 and value < float(averages.iloc[ind]['Avg']):
                beat_number += 1
                finrat_beats.append(averages.iloc[ind]['Type'])
        if ind == 18 or ind == 19:
            if value != 0 and value > float(averages.iloc[ind]['Avg']):
                beat_number += 1
                dbt_beats.append(averages.iloc[ind]['Type'])
        if ind == 20 or ind == 21:
            if value < float(averages.iloc[ind]['Avg']):
                beat_number += 1
                dbt_beats.append(averages.iloc[ind]['Type'])
        if ind > 21:
            if value > float(averages.iloc[ind]['Avg']):
                beat_number += 1
                marg_beats.append(averages.iloc[ind]['Type'])
            
    if beat_number < 6:
        sentiment = ('Poorly', C)
    elif beat_number < 10: 
        sentiment = ('Fairly', 'B')
    else: 
        sentiment = ('Favorably', 'A')
        
    return(beat_number, sentiment, finrat_beats, dbt_beats, marg_beats)

# Simple formatting function to change all table values to floats for calculation purposes
def format_data_to_floats(table):
    for col in table:
        table[col] = table[col].str.strip("%").replace('-',0)
        table[col] = pd.to_numeric(table[col], errors='ignore')
        
# Formatting for urls        
def format(data_string):
    return(data_string.lower().replace(" ","").replace("-","").replace("&",""))        

# Fast method for assigning a color to the plotly graphs
def get_chart_color(tick_index, graph_num):
    color_options = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd','#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

    colors = [color_options[graph_num],]*len(comp_data.index)
    colors[tick_index] = 'gold'
    
    return(colors)
