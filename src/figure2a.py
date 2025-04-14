# Standard Library Imports (if any)

# Third-party Library Imports
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
from IPython.display import display, HTML
from adjustText import adjust_text
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.outliers_influence import variance_inflation_factor

# Local Module Imports
from data_handling import *
from data_handling.data_processor import *
from plot import *
from utils import *

def run_figure2a(save=None, period=None):
    major = COUNTRIES.MAJOR
    offshore = COUNTRIES.OFFSHORE
    period = (None, None) if period is None else period
    dm = DataManager(
        raw_dir = "./data/raw",
        save_dir = "./data/clean"
    )
    ds_full = dm.sources["ds"].filter_period(period)
    fed_full = dm.sources["fed"].filter_period(period)
    dm.filter_data(None, (2001, 2004))

    # Access datasets
    cpis = dm.get_dataset("cpis")
    ds = dm.get_dataset("ds")
    fed = dm.get_dataset("fed")
    wb = dm.get_dataset("wb")
    wfe = dm.get_dataset("wfe")
    gdp = dm.get_dataset("gdp")
    gdppc = dm.get_dataset("gdppc")

    index_excess_returns = compute_index_excess_returns(ds_full, fed_full, major)
    # index_excess_returns = compute_index_excess_returns(ds, fed, major)
    weights = compute_weights(cpis, wb, major, offshore).mean(axis=1).unstack(level="Country")
    return_statistics = compute_excess_returns_statistics(index_excess_returns, weights)
    domestic_investments = compute_domestic_investments(cpis, wb, major).droplevel(1)
    total_outward_investments = cpis.get_data(holders=major, issuers="WR").droplevel(1)
    total_investments = domestic_investments + total_outward_investments  

    y = total_investments / gdp; y = y.mean(axis=1)
    X_1 = gdppc.mean(axis=1)
    X_2 = return_statistics["mean_portfolio"]
    X_3 = return_statistics["var_portfolio"]
    X = pd.concat([X_1, X_2, X_3], axis=1, keys=["gdp/cap", "mean", "var"])

    X=(X-X.mean())/X.std() # Normalize
    # X["gdp/cap"] /= 1e4
    # X[["mean", "var"]] *= 1e2
    X = sm.add_constant(X).sort_index()

    vif_data = pd.DataFrame()
    vif_data["feature"] = X.columns
    vif_data["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
    print(vif_data)

    cov_type = "HAC"
    cov_kwds = {"maxlags": 0} if cov_type == "HAC" else {}
    model = sm.OLS(y, X).fit(cov_type=cov_type, cov_kwds=cov_kwds)
    print(model.summary())

    if save is not None:
        save_dir = f"./output/exp2/results/"
        os.makedirs(save_dir, exist_ok=True)
        
        with open(os.path.join(save_dir, f"{save}.txt"), "w") as f:
            f.write(model.summary().as_text())

if __name__ == "__main__":
    run_figure2a(save="2a_short", period=(2001, 2004))
    run_figure2a(save="2a_long", period=(None, 2004))
