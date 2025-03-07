import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import numpy as np
from data.manager import *
from utils import *
from adjustText import adjust_text
from plot.plot import scatter_countries

data = DataManager(
    raw_dir = "./data/raw",
    save_dir = "./data/clean"
)
data.load_data()

ds = data.get_dataset("ds")
fed = data.get_dataset("fed")
cpis = data.get_dataset("cpis")
wb = data.get_dataset("wb")

# Align the risk-free rate data with the returns data
start, end = (2001, 2004)
ds = ds.loc[:, (ds.columns >= pd.Timestamp(f"{start-1}-12-01")) & (ds.columns <= pd.Timestamp(f"{end+1}-01-01"))]
fed = fed.reindex(columns=ds.columns)
fed = annual_to_monthly_return(fed)

# Calculate returns and risk-free rate
ds_filled = ds.ffill(axis=1)
returns = ds_filled.pct_change(axis=1, fill_method=None)
riskfree_rate = fed.loc["FEDFUNDS"]
avg_riskfree_rate = riskfree_rate.mean() 

# Simple excess returns
excess_returns = returns.subtract(riskfree_rate, axis=1)
mean_excess = excess_returns.mean(axis=1)
var_excess = excess_returns.var(axis=1)
cov_excess = pd.Series(cpis.calculate_cov_index_portfolio(wb, fed, ds, (start, end), False), index=DS.CODES)

# Log excess returns
log_returns = np.log(1 + returns)
log_risk_free = np.log(1 + riskfree_rate)
log_excess_returns = log_returns.subtract(log_risk_free, axis=1)
mean_log_excess = log_excess_returns.mean(axis=1)
var_log_excess = log_excess_returns.var(axis=1)
cov_log_excess = pd.Series(cpis.calculate_cov_index_portfolio(wb, fed, ds, (start, end), True), index=DS.CODES)


scatter_countries(x=var_excess,
                  y=mean_excess,
                  codes=DS.CODES,
                  x_label="Variance of returns",
                  y_label="Mean return",
                  title="Monthly excess returns (USD)",
                  save="fig1a",
                  riskfree=avg_riskfree_rate,
                  )

scatter_countries(x=var_log_excess,
                  y=mean_log_excess,
                  codes=DS.CODES,
                  x_label="Variance of log returns",
                  y_label="Mean log return",
                  title="Monthly log excess returns (USD)",
                  save="fig1a_log",
                  riskfree=avg_riskfree_rate,
                  )

scatter_countries(x=cov_excess,
                  y=mean_excess,
                  codes=DS.CODES,
                  x_label="Covariance between excess returns of country's index and country's portfolio",
                  y_label="Mean return",
                  title="Monthly excess returns (USD)",
                  save="fig1b",           
                  riskfree=avg_riskfree_rate,
                  )

scatter_countries(x=cov_log_excess,
                  y=mean_log_excess,
                  codes=DS.CODES,
                  x_label="Covariance between log excess returns of country's index and country's portfolio",
                  y_label="Mean log excess return",
                  title="Monthly log excess returns (USD)",
                  save="fig1b_log",
                  riskfree=avg_riskfree_rate,
                  )