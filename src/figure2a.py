# Standard Library Imports (if any)

# Third-party Library Imports
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from IPython.display import display, HTML
from adjustText import adjust_text
from statsmodels.stats.outliers_influence import variance_inflation_factor
from linearmodels.panel import PanelOLS, PooledOLS, RandomEffects

# Local Module Imports
from utils import *
from new_data_handling import DataManager
from plot import *
from new_data_handling.data_processor import *

def run_figure2a(save=None):
    major = COUNTRIES.MAJOR
    offshore = COUNTRIES.OFFSHORE
    dm = DataManager(
        raw_dir = "./data/raw",
        save_dir = "./data/clean"
    )

    # Weights
    period = (2001,2004)
    cpis = dm.cpis.get_data(period=period)
    wb = dm.wb.get_data(countries=major, period=period)
    weights = compute_weights(cpis, wb, major, offshore).mean(axis=1).unstack(level="Country")  
    
    # Returns
    period = (1990, 2004)
    ds = dm.ds.get_data(countries=major, period=period)
    fed = dm.fed.get_data(period=period)

    years = [2001, 2002, 2003, 2004]
    for year in years:
        period = (year,year)
        gdp = dm.gdp.get_data(countries=major, period=period, gdp_type="gdp")
        gdp_cap_ppp = dm.gdp.get_data(countries=major, period=period, gdp_type="gdp_cap_ppp")
        cpis = dm.cpis.get_data(period=period)
        wb = dm.wb.get_data(countries=major, period=period)
        domestic_investments = compute_domestic_investments(cpis, wb, major).droplevel(1)
        total_outward_investments = cpis.get_data(countries=major, counterparts="WR").droplevel(1)
        total_investments = domestic_investments + total_outward_investments

        ds_year = ds.get_data(period=(year-4, year), interval="M")
        fed_year = fed.get_data(period=(year-4, year))
        index_excess_returns = compute_index_excess_returns(ds_year, fed_year, major)
        return_statistics = compute_excess_returns_statistics(index_excess_returns, weights)

        y = (total_investments / gdp)
        X_1 = gdp_cap_ppp
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
            
            with open(os.path.join(save_dir, f"{save}_{year}.txt"), "w") as f:
                f.write(model.summary().as_text())

if __name__ == "__main__":
    run_figure2a(save="2a")