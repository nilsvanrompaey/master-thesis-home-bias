# Standard Library Imports (if any)

# Third-party Library Imports
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from IPython.display import display, HTML
from adjustText import adjust_text
from statsmodels.stats.outliers_influence import variance_inflation_factor
from linearmodels.panel import PanelOLS, PooledOLS

# Local Module Imports
from data_handling import *
from data_handling.data_processor import *
from plot import *
from utils import *

major = COUNTRIES.MAJOR
offshore = COUNTRIES.OFFSHORE
sample = major + offshore
period = (2001, 2004)
dm = DataManager(
    raw_dir = "./data/raw",
    save_dir = "./data/clean"
)

ds_year = {}
fed_year = {}
for year in range(2004, 2000, -1):
    ds_year[year] = dm.sources["ds"].filter_period((None, year))
    fed_year[year] = dm.sources["fed"].filter_period((None, year))

dm.filter_data(None, period)

# Access datasets
cpis = dm.get_dataset("cpis")
ds = dm.get_dataset("ds")
fed = dm.get_dataset("fed")
wb = dm.get_dataset("wb")
wfe = dm.get_dataset("wfe")
gdp = dm.get_dataset("gdp")
gdppc = dm.get_dataset("gdppc")

domestic_investments = compute_domestic_investments(cpis, wb, major).droplevel(1)
total_outward_investments = cpis.get_data(holders=major, issuers="WR").droplevel(1)
total_investments = domestic_investments + total_outward_investments
weights = compute_weights(cpis, wb, major, offshore).mean(axis=1).unstack(level="Country")

y = (total_investments / gdp).stack() 
X_1 = gdppc.stack().rename("gdp/cap", inplace=True)
X_2 = pd.DataFrame(index=X_1.index, columns=["mean"])
X_3 = pd.DataFrame(index=X_1.index, columns=["var"])

years = [2001, 2002, 2003, 2004]
for year in years:
    index_excess_returns = compute_index_excess_returns(ds_year[year], fed_year[year], major)
    return_statistics = compute_excess_returns_statistics(index_excess_returns, weights)
    X_2.loc[(slice(None), year), :] = return_statistics["mean_portfolio"].values
    X_3.loc[(slice(None), year), :] = return_statistics["var_portfolio"].values

X = pd.concat([X_1, X_2, X_3], axis=1)
# X = pd.DataFrame(X_1, columns=['gdp/cap'])
X = (X-X.mean())/X.std() # Normalize
X = sm.add_constant(X)

model_panel = PanelOLS(y, X, entity_effects=True).fit(cov_type="kernel", kernel="bartlett", bandwidth=1)
print(model_panel.summary)


save = "2b"
save=None
if save is not None:
    save_dir = f"./output/exp2/results/"
    os.makedirs(save_dir, exist_ok=True)
    
    with open(os.path.join(save_dir, f"{save}.txt"), "w") as f:
        f.write(model_panel.summary.as_text())