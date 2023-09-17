# -*- coding: utf-8 -*-
"""Markowitz_Opt.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1eaB0vxWyPu-9866Oo9zykPYbi7AKpda5
"""

!pip install pyPortfolioOpt
!pip install yfinance

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas_datareader.data as web
import datetime
import yfinance as yf
yf.pdr_override()

# %matplotlib inline

#Past data period selected
start_date = datetime.datetime(2023,4,1)
end_date = datetime.datetime(2023,8,30)

#Taking data from Yahoo Finance
def get_stock_price(ticker):
    prices = web.get_data_yahoo(ticker,start_date,end_date)
    prices = prices["Adj Close"].dropna(how="all")
    return prices

#In here I considered stock prices of Indian Stock Market
ticker_list = ['INFY.NS','RELIANCE.NS','TCS.NS','HDFCBANK.NS','HINDUNILVR.NS','LT.NS','HCLTECH.NS','BAJAJFINSV.NS','KOTAKBANK.NS','TITAN.NS']
portfolio = get_stock_price(ticker_list)
portfolio

#portfolio.to_csv("portfolio.csv",index=True)
#portfolio = pd.read_csv("portfolio.csv",parse_dates=True,index_col="Date")

portfolio[portfolio.index >= "2023-04-01"].plot(figsize=(12,8));

import pypfopt
from pypfopt import risk_models
from pypfopt import plotting

#Calculating sample covarianve
sample_cov = risk_models.sample_cov(portfolio)
sample_cov

#Covariance matrix
S = risk_models.CovarianceShrinkage(portfolio).ledoit_wolf()
plotting.plot_covariance(S, plot_correlation=True);

#This is optional
correlation_matrix = risk_models.cov_to_corr(sample_cov)
correlation_matrix

#Calculating expected returns
from pypfopt import expected_returns
#mu = expected_returns.mean_historical_return(portfolio) You are able to use mean hostorical return or CAPM to find expected returns.
mu = expected_returns.capm_return(portfolio)
mu

mu.plot.barh(figsize=(5,5));

#Fining best allocation
from pypfopt.efficient_frontier import EfficientFrontier

ef = EfficientFrontier(mu, S, weight_bounds=(0, 1))
weights = ef.max_sharpe()

cleaned_weights = ef.clean_weights()
numerical_weights = np.array([value for value in cleaned_weights.values()])
print(dict(cleaned_weights))

#Another method of finding the allocations
from pypfopt import objective_functions
from pypfopt.efficient_frontier import EfficientFrontier

ef1 = EfficientFrontier(mu, S, weight_bounds=(0, 1))
ef1.add_objective(objective_functions.L2_reg, gamma=0.5)
weights1 = ef1.max_sharpe()
cleaned_weights1 = ef1.clean_weights()
numerical_weights1 = np.array([value for value in cleaned_weights1.values()])
print(cleaned_weights1)

#Finding the portfolio return and risk with traditional calculations
risk_free_rate = 0.02
# Calculate the portfolio return
portfolio_return = np.dot(list(cleaned_weights.values()), mu)
portfolio_return

# Calculate the portfolio standard deviation
portfolio_std_dev = np.sqrt((numerical_weights.T * (S @ numerical_weights.T)).sum(axis=0))

# Calculate the Sharpe ratio
sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_std_dev

print("Portfolio_Return:", portfolio_return*100,"%")
print("Portfolio_Std:", portfolio_std_dev*100,"%")
print("Sharpe Ratio:", sharpe_ratio)

#Calculate the above 3 results using inbuilt functions
ef.portfolio_performance(verbose=True)

#Finding the allocation
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices

latest_prices = get_latest_prices(portfolio)

da = DiscreteAllocation(weights, latest_prices, total_portfolio_value=100000)

# Number of shares of each stock to purchase
allocation, leftover = da.greedy_portfolio()
print("Discrete allocation:", allocation)
print("Funds remaining: ${:.2f}".format(leftover))

#Plotting
n_samples = 10000
w = np.random.dirichlet(np.ones(len(mu)), n_samples)
rets = w.dot(mu)
stds = np.sqrt((w.T * (S @ w.T)).sum(axis=0))
sharpes = (rets-0.02) / stds
#print("Sample portfolio returns:", rets)
#print("sharpe ratio:", sharpes)
#print("Sample portfolio volatilities:", stds)

# Plot efficient frontier with Monte Carlo sim
ef = EfficientFrontier(mu, S, weight_bounds=(0, 1))

fig, ax = plt.subplots(figsize= (5,5))
plotting.plot_efficient_frontier(ef, ax=ax, show_assets=False)

# Find and plot the tangency portfolio
ef2 = EfficientFrontier(mu, S)
ef2.max_sharpe()
ret_tangent, std_tangent, _ = ef2.portfolio_performance()

# Plot random portfolios
ax.scatter(stds, rets, marker=".", c=sharpes, cmap="viridis_r")
ax.scatter(std_tangent, ret_tangent, c='red', marker='X',s=150, label= 'Max Sharpe')

# Format
ax.set_title("Efficient Frontier with random portfolios")
ax.legend()
plt.tight_layout()
plt.show()

