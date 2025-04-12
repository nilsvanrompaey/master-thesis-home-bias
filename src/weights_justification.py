# Standard Library Imports (if any)

# Third-party Library Imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from IPython.display import display, HTML
from adjustText import adjust_text
from sklearn.preprocessing import StandardScaler

# Local Module Imports
from utils import *
from data_handling import *
from plot import *
from data_handling.data_processor import *

major = COUNTRIES.MAJOR
offshore = COUNTRIES.OFFSHORE
sample = major + offshore

major = COUNTRIES.MAJOR
offshore = COUNTRIES.OFFSHORE
sample = major + offshore
period = (2001, 2004)
dm = DataManager(
    raw_dir = "./data/raw",
    save_dir = "./data/clean"
)
ds_full = dm.get_dataset("ds")
fed_full = dm.get_dataset("fed")
# dm.clean_data()
# dm.save_data()
dm.filter_data(None, period)

# Access datasets
cpis = dm.get_dataset("cpis")
ds = dm.get_dataset("ds")
fed = dm.get_dataset("fed")
wb = dm.get_dataset("wb")
wfe = dm.get_dataset("wfe")
gdp = dm.get_dataset("gdp")

weights_per_year = compute_weights(cpis, wb, major, offshore)
weights_dict = {}
for year in weights_per_year.columns:
    weights_dict[year] = weights_per_year[year].unstack("Country")
weights_avg = weights_per_year.mean(axis=1).unstack("Country")
index_returns = compute_index_excess_returns(ds, fed ,major)

means = pd.DataFrame(index=major)
vars = pd.DataFrame(index=major)
covs = pd.DataFrame(index=major)

for year, weights in weights_dict.items():
    returns = compute_excess_returns_statistics(index_returns, weights)
    means[year] = returns["mean_portfolio"]
    vars[year] = returns["var_portfolio"]  
    covs[year] = returns["cov_index_portfolio"]

returns = compute_excess_returns_statistics(index_returns, weights_avg)
means_avg = returns["mean_portfolio"]
vars_avg = returns["var_portfolio"]  
covs_avg = returns["cov_index_portfolio"]

print((means.var(axis=1) / (vars_avg / 48)))
print((means.var(axis=1) / (vars_avg / 48)).mean())
print((means.var(axis=1) / (vars_avg / 48)).max())