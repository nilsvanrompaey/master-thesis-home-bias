# Standard Library Imports (if any)

# Third-party Library Imports
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from IPython.display import display, HTML
from adjustText import adjust_text
from statsmodels.stats.outliers_influence import variance_inflation_factor
from linearmodels.panel import PanelOLS

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
ds_full = dm.sources["ds"].filter_period((None, 2004))
fed_full = dm.sources["fed"].filter_period((None, 2004))
dm.filter_data(None, period)

# Access datasets
cpis = dm.get_dataset("cpis")
ds = dm.get_dataset("ds")
fed = dm.get_dataset("fed")
wb = dm.get_dataset("wb")
wfe = dm.get_dataset("wfe")
gdp = dm.get_dataset("gdp")
gdppc = dm.get_dataset("gdppc")

index_excess_returns = compute_index_excess_returns(ds_full, fed_full, major)
weights = compute_weights(cpis, wb, major, offshore).mean(axis=1).unstack(level="Country")
return_statistics = compute_excess_returns_statistics(index_excess_returns, weights)
domestic_investments = compute_domestic_investments(cpis, wb, major).droplevel(1)

y = (domestic_investments / gdp).stack() 
X_1 = gdppc.stack()
X_2 = return_statistics["mean_portfolio"]
X_3 = return_statistics["var_portfolio"]
years = [2001, 2002, 2003, 2004]
multi_index = pd.MultiIndex.from_product([X_2.index, years], names=['Country', 'Year'])
X_2 = pd.Series(
    X_2.values.repeat(len(years)),
    index=multi_index,
    name='Value'
)
X_3 = pd.Series(
    X_3.values.repeat(len(years)),
    index=multi_index,
    name='Value'
)
X = pd.concat([X_1, X_2, X_3], axis=1, keys=["gdp/cap", "mean", "var"])
# X = pd.DataFrame(X_1, columns=['gdp/cap'])
X = (X-X.mean())/X.std() # Normalize
X = sm.add_constant(X)

fe_model = PanelOLS(y, X, entity_effects=True, time_effects=True, drop_absorbed=True).fit()
print(fe_model.summary)

# fixed_effects = fe_model.estimated_effects.unstack(level="time").iloc[:,0]
# X = pd.concat([X_2, X_3], axis=1, keys=["mean", "var"])
# X = (X-X.mean())/X.std() # Normalize
# X = sm.add_constant(X)
# model_2 = sm.OLS(fixed_effects, X).fit()
# print(model_2.summary())


import numpy as np
from scipy import stats
from linearmodels.panel import RandomEffects

re_model = RandomEffects(y,X).fit()
# Get the coefficients and covariance matrices of both models
fe_coeffs = fe_model.params
re_coeffs = re_model.params

fe_cov = fe_model.cov
re_cov = re_model.cov

# Calculate the Hausman test statistic
diff = fe_coeffs - re_coeffs
cov_diff = np.linalg.inv(fe_cov) - np.linalg.inv(re_cov)
hausman_stat = np.dot(np.dot(diff.T, np.linalg.inv(cov_diff)), diff)

# Degrees of freedom for the test is the number of parameters estimated (length of diff)
df = len(diff)

# Calculate the p-value
p_value = 1 - stats.chi2.cdf(hausman_stat, df)

print(f"Hausman test statistic: {hausman_stat}")
print(f"P-value: {p_value}")