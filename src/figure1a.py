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

# Align the risk-free rate data with the returns data
fed = fed.reindex(columns=ds.columns)
fed = annual_to_monthly_return(fed)

# Calculate returns and risk-free rate
returns = ds.pct_change(axis=1, fill_method="ffill")
risk_free_rate = fed.loc["FEDFUNDS"]

# Simple excess returns
excess_returns = returns.subtract(risk_free_rate, axis=1)
mean_excess = excess_returns.mean(axis=1)
var_excess = excess_returns.var(axis=1)

# Log excess returns
log_returns = np.log(1 + returns)
log_risk_free = np.log(1 + risk_free_rate)
log_excess_returns = log_returns.subtract(log_risk_free, axis=1)
mean_log_excess = log_excess_returns.mean(axis=1)
var_log_excess = log_excess_returns.var(axis=1)
    
scatter_countries(x=var_excess,
                  y=mean_excess,
                  codes=DS.CODES,
                  x_label="Variance",
                  y_label="Mean",
                  title="Monthly log excess returns (USD)",
                  save="fig1a",)

scatter_countries(x=var_log_excess,
                  y=mean_log_excess,
                  codes=DS.CODES,
                  x_label="Variance",
                  y_label="Mean",
                  title="Monthly log excess returns (USD)",
                  save="fig1a_log",)