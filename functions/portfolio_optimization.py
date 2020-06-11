#!/usr/bin/env python
# coding: utf-8

# # Portfolio Optimization 
# ## Employing the Efficient Frontier and Risk-Parity Methods
# 
# Financial data is pulled and parsed using **python datareader** from **yahoo finance**.
# 
# #### Built With
#  * Python 3
#  * MatPlotLib
# 
# ###### Written by: Jake Robinson (https://github.com/jakerobinson19)


#import relevant modules and packages
import numpy as np
import pandas as pd
from datetime import datetime
from pandas_datareader import data as wb
import matplotlib.pyplot as plt

class Portfolio:

    def __init__(self, assets, percentages, date):
        self.assets = assets
        self.percentages = np.array(percentages)
        self.start_date = date
        
        self.historical_asset_prices = self.get_historical_prices(assets, date)
        self.historical_daily_returns = self.get_daily_returns(historical_asset_prices)


    # Grab the historical Adj Close data for each stock from yahoo
    def get_historical_prices(self, assets, start_date):
        data = pd.DataFrame()

        for i in assets:
            data[i] = wb.DataReader(i, data_source='yahoo', start=start_date)['Adj Close']

        return(data)

    # Plot the overlapping stock charts
    def plot_stock_chart(self):
        plt.figure(figsize=(16,8)) 

        for i in assets:
            plt.plot(self.historical_daily_returns.index, self.historical_asset_prices[i])
 
        plt.legend(self.historical_asset_prices.columns, fontsize=16)
        plt.show()

    # Calculate daily returns for each asset in the portfolio
    def get_daily_returns(self, data):
        return(np.log(data/data.shift(1)))

    def get_theoretical_returns(self, start_date=self.start_date, dollars=1000):
        print("Total returns for each security (assuming they were bought on the start date of {})\n".format(start_date))

        dollars_in_assets = self.percentages*dollars

        for i, stock in enumerate(self.assets):
    
            tot_return = ((self.historical_asset_prices[stock][-1] - self.historical_asset_prices[stock][0])/self.historical_asset_prices[stock][0])*100
            print("{}: {}%".format(stock, round(tot_return, 2)))
            dollars_in_assets[i] = dollars_in_assets[i]*(tot_return/100)    
    
        print("\nIf you had invested $1000 dollars on {} in these assets with the specified portfolio percentages above,\nit would be worth ${} today".format(data.index[0].strftime("%Y-%m-%d"), round(dollars_in_assets.sum(),2)))

    def get_expected_portfolio_return(self):
        return(np.sum(self.percentages * self.historical_daily_returns.mean()) * 250)

    def get_expected_portfolio_variance(self):
        return(np.dot(self.percentages.T, np.dot(self.historical_daily_returns.cov() *250, self.percentages)))

    def get_expected_portfolio_volatility(self):
        return(np.sqrt(np.dot(self.percentages.T, np.dot(self.historical_daily_returns.cov() *250, self.percentages))))


class Optimizer:

    def __init__(portfolio):
        self.portfolio = portfolio
        self.returns = portfolio.historical_daily_returns
        self.num_assets = len(portfolio.assets)

        self.pfolio_returns = []
        self.pfolio_vols = []
        self.sharpe_arr = []

    def run_optimization_simulations(self):
        all_weights = np.zeros((10000,len(self.returns.columns)))

        #create array of returns and volatilities for each of the 1000 simulations
        for x in range (10000):
            weights = np.random.random(self.num_assets)
            weights /= np.sum(weights)
    
            # Save Weights
            all_weights[x,:] = weights
    
            # Portfolio return and volatility
            self.pfolio_returns.append(np.sum(weights * self.returns.mean()) * 250)
            self.pfolio_vols.append(np.sqrt(np.dot(weights.T, np.dot(self.returns.cov() *250, weights))))
    
            # Sharpe Ratio
            self.sharpe_arr.append(self.pfolio_returns[x]/self.pfolio_vols[x])

        #convert arrays in numpy arrays
        self.pfolio_returns = np.array(self.pfolio_returns)
        self.pfolio_vols = np.array(self.pfolio_vols)

        #set optimal blend
        self.optimal_blend = all_weights[self.sharpe_arr.index(max(self.sharpe_arr))]*100

    def get_max_sharpe_ratio_info(self)
        max_sr_ret = self.pfolio_returns[self.sharpe_arr.index(max(sharpe_arr))]

        max_sr_vol = self.pfolio_vols[self.sharpe_arr.index(max(sharpe_arr))]

        return(max_sr_ret, max_sr_vol)

    def get_optimal_blend(self):
        return(self.optimal_blend)

    def graph_efficient_frontier(self):
        plt.figure(figsize=(14,8))
        plt.scatter(self.pfolio_vols,self.pfolio_returns,c=self.sharpe_arr,cmap='spring')
        plt.colorbar(label='Sharpe Ratio')
        plt.xlabel('Volatility')
        plt.ylabel('Return')

        # Add red dot for max SR (optimal risk/reward)
        plt.scatter(self.max_sr_vol,self.max_sr_ret,c='red',s=50,edgecolors='black',cmap='plasma')

    def generate_risk_parity(self):
        # risks associated with each security
        vol = self.returns.rolling(window=252).std() * np.sqrt(252)
        self.rp_vols = vol.tail(1).values

        # get the inverse of the individual volatilies
        inv_vol = 1/rp_vols

        # sum up these inverses
        inv_vol.sum()

        # calculate the risk parity percentage by dividing the inverse volatility by the sum
        self.rp_weights = inv_vol/inv_vol.sum()

    def get_risk_parity_allocation(self):
        return(self.rp_weight[0])

    # Set up figure to visualize the risk of each asset in the portfolio
    def graph_asset_risk(self):
        fig = plt.figure()
        ax = fig.add_axes([0,0,1,1])
        ax.bar(assets, height=self.rp_vols[0], width=0.5, color='r')
        ax.set_title('RISK')
        plt.show()

    def graph_risk_parity_allocation(self):
        fig = plt.figure()
        ax = fig.add_axes([0,0,1,1])
        ax.bar(assets, height=self.rp_weights[0], width=0.5, color='g')
        vals = ax.get_yticks()
        ax.set_yticklabels(['{:,.2%}'.format(x) for x in vals])
        ax.set_title('RISK-PARITY PORTFOLIO ALLOCATION')
        plt.show()

    def print_conclusion(self):

        print("The inputed portfolio consisting of: \n")

        for ind, value in enumerate(self.portfolio.percentages*100):
            print("{}% {}".format(round(value, 2), self.portfolio.assets[ind]))
    
        print("\nProvides an expected return of {}% with volatility of {}%.".format(round(np.sum(self.portfolio.percentages * self.returns.mean()) * 25000, 2),
                                                                      round(np.sqrt(np.dot(self.portfolio.percentages.T, np.dot(self.returns.cov() *250, self.portfolio.percentages)))*100,2)))
        print("\nMarkowitz Model (Efficient Frontier)\n")
        for ind, value in enumerate(self.optimal_blend):
            print("{}% {}".format(round(value, 2), self.portfolio.assets[ind]))
    
        print("\nThis optimal blend offers the most efficient option by balancing the expected return and volatility.")
        print("The expected return of this portfolio is {}% with a volality of {}%.".format(round(self.pfolio_returns[self.sharpe_arr.index(max(self.sharpe_arr))]*100,2),
                                                                                  round(self.pfolio_vols[self.sharpe_arr.index(max(self.sharpe_arr))]*100),2))
        print("These values were chosen by computing the maximum Sharpe Ratio for all simulations. \nThe corresponding ratio value for this blend in {}.".format(round(max(self.sharpe_arr),3)))

        print("\nRisk-Parity Portfolio")
        print("\nThe risk-parity method, which seeks to optimize returns while adhering to market risk parameters, indicates the following blend will be the best and most resilient option:\n")

        for ind, value in enumerate(self.portfolio.percentages*100):
            print("{}% {}".format(round(self.rp_weights[0][ind]*100, 2), self.portfolio.assets[ind]))
