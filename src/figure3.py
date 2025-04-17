# Standard Library Imports (if any)

# Third-party Library Imports
import pandas as pd
import statsmodels.api as sm
from linearmodels.panel import PanelOLS

# Local Module Imports
from utils import *
from new_data_handling import DataManager
from plot import *
from new_data_handling.data_processor import *

major = COUNTRIES.MAJOR
offshore = COUNTRIES.OFFSHORE
sample = major + offshore
period = (2001, 2004)
dm = DataManager(
    raw_dir = "./data/raw",
    save_dir = "./data/clean"
)

period = (2001, 2004)
cpis = dm.cpis.get_data(period=period)
wb = dm.wb.get_data(countries=major, period=period)
weights = compute_weights(cpis, wb, major, offshore).mean(axis=1).unstack(level="Country")

# Index returns
period = (2001, 2004)
ds = dm.ds.get_data(period=period, interval="M")
fed = dm.fed.get_data(period=period)
panel_dates = fed.columns
returns_index = compute_index_excess_returns(ds, fed, major)
# returns_portfolio = compute_portfolio_excess_returns(ds, fed, major, weights)
returns_index = returns_index.stack().rename("returns")

# World market return
returns_world = [
    0.012210012, -0.075995175, -0.081636205, 0.078278999, -0.01529267, -0.030167797, -0.025860482, -0.038072744, -0.090846592, 0.018796586,
    0.058106245, 0.005210943, -0.031901107, -0.012974977, 0.047052686, -0.0354723, -0.000929752, -0.059766312, -0.086880018, 0.001083946,
    -0.112367661, 0.073597181, 0.048478727, -0.045875978, -0.030413932, -0.035012365, 0.033989749, 0.061440125, 0.054565565, 0.016315115,
    0.018117188, 0.019258926, 0.005635359, 0.057136578, 0.014759381, 0.060432244, 0.017772626, 0.016228528, -0.01690325, -0.004179728,
    -0.004769627, 0.019457491, -0.042967281, 0.014441497, 0.007747434, 0.026619258, 0.060376299, 0.029131356
]
returns_world_dummies = pd.DataFrame(0.0, index=returns_index.index, columns=major)
for country in major:
    returns_world_dummies.loc[(country, slice(None)), country] = returns_world
returns_world_dummies.columns = ['WRx' + str(col) for col in returns_world_dummies.columns]

# GDP per capita
interpolate = False
period = (2001, 2004) if not interpolate else (2000,2004)
gdp_cap_ppp = dm.gdp.get_data(countries=major, period=period, gdp_type="gdp_cap_ppp")
gdp_cap_ppp = create_monthly_duplicates(gdp_cap_ppp, panel_dates, interpolate=interpolate)
gdp_cap_ppp = gdp_cap_ppp.stack().rename("gdp_cap")

# GDP growth
n_lags = 5
interpolate = False
gdp_ppp_lag = pd.DataFrame(0.0, index=returns_index.index, columns=range(n_lags))
for lag in range(n_lags):
    period = (2000-lag,2004-lag)
    gdp_ppp = dm.gdp.get_data(countries=major, period=period, gdp_type="gdp_ppp")
    gdp_ppp = (gdp_ppp.diff(axis=1) / gdp_ppp).iloc[:,1:]
    gdp_ppp = create_monthly_duplicates(gdp_ppp, panel_dates, interpolate=interpolate)
    gdp_ppp_lag[lag] = gdp_ppp.stack().rename(f"lag{lag}")

# variances (rolling window, exponential decay)
period = (1996,2004)
ds = dm.ds.get_data(period=period, interval="M")
fed = dm.fed.get_data(period=period)
returns_index_historical = compute_index_excess_returns(ds, fed, major)
variances = pd.DataFrame(index=major, columns=panel_dates)
for i in range(48):
    returns = returns_index_historical.iloc[:,i:i+60]
    means = returns.mean(axis=1)
    returns_demeaned = returns.sub(means, axis=0)
    var_contributions = returns_demeaned**2
    factors = generate_exponential_decay()
    vars = var_contributions.mul(factors).sum(axis=1) / sum(factors)
    variances.iloc[:,i] = vars
variances = variances.stack().rename("variances")


y = returns_index * 1e2
X = pd.concat([
        returns_world_dummies * 1e2, 
        gdp_cap_ppp / 1e5,
        gdp_ppp_lag *1e2,
        variances * 1e4,
],
    axis=1)
X = sm.add_constant(X)
from linearmodels.panel import PanelOLS, PooledOLS

model_panel = PanelOLS(y, X, entity_effects=True).fit(cov_type="kernel", kernel="bartlett", bandwidth=4)
model_pooled = PooledOLS(y,X).fit(cov_type="kernel", kernel="bartlett", bandwidth=4)

model_panel.summary
model_pooled.summary

comparison = pd.DataFrame([model_pooled.params, model_panel.params], index=["pooled", "panel"])
date = model_panel.estimated_effects.index.get_level_values(1)[0]

effects = model_panel.estimated_effects.loc[(slice(None), date),:].droplevel(1)
