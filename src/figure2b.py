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

def run_figure2b(save=None, justification=False):
    major = COUNTRIES.MAJOR
    offshore = COUNTRIES.OFFSHORE
    sample = major + offshore
    period = (2001, 2004)
    dm = DataManager(
        raw_dir = "./data/raw",
        save_dir = "./data/clean"
    )

    save = "2b"
    justification = True
    period = (2001,2004)
    cpis = dm.cpis.get_data(period=period)
    wb = dm.wb.get_data(countries=major, period=period)
    gdp = dm.gdp.get_data(countries=major, period=period, gdp_type="gdp")
    gdp_cap = dm.gdp.get_data(countries=major, period=period, gdp_type="gdp_cap")

    domestic_investments = compute_domestic_investments(cpis, wb, major).droplevel(1)
    total_outward_investments = cpis.get_data(countries=major, counterparts="WR").droplevel(1)
    total_investments = domestic_investments + total_outward_investments
    weights = compute_weights(cpis, wb, major, offshore).mean(axis=1).unstack(level="Country")
    y = (total_investments / gdp).stack() 
    X_1 = gdp_cap.stack().rename("gdp/cap", inplace=True)
    X_2 = pd.DataFrame(index=X_1.index, columns=["mean"])
    X_3 = pd.DataFrame(index=X_1.index, columns=["var"])
    period = (1990, 2004)
    ds = dm.ds.get_data(countries=major, period=period)
    fed = dm.fed.get_data(period=period)
    ds_year = {}
    fed_year = {}
    years = [2001, 2002, 2003, 2004]
    for year in years:
        ds_year[year] = ds.get_data(period=(year-4, year), interval="M")
        fed_year[year] = fed.get_data(period=(year-4, year))

    for year in years:
        index_excess_returns = compute_index_excess_returns(ds_year[year], fed_year[year], major)
        return_statistics = compute_excess_returns_statistics(index_excess_returns, weights)
        X_2.loc[(slice(None), year), :] = return_statistics["mean_portfolio"].values
        X_3.loc[(slice(None), year), :] = return_statistics["var_portfolio"].values
    X = pd.concat([X_1, X_2, X_3], axis=1)
    # X = pd.DataFrame(X_1, columns=['gdp/cap'])
    X = (X-X.mean())/X.std() # Normalize
    X = sm.add_constant(X)

    model_panel_e = PanelOLS(y, X, entity_effects=True).fit(cov_type="kernel", kernel="bartlett", bandwidth=0)
    print(model_panel_e.summary)

    if save is not None:
        save_dir = f"./output/exp2/results/"
        os.makedirs(save_dir, exist_ok=True)
        
        with open(os.path.join(save_dir, f"{save}.txt"), "w") as f:
            f.write(model_panel_e.summary.as_text())

    if justification:
        model_panel_t = PanelOLS(y, X, time_effects=True).fit(cov_type="kernel", kernel="bartlett", bandwidth=0)
        model_panel_et = PanelOLS(y, X, entity_effects=True, time_effects=True).fit(cov_type="kernel", kernel="bartlett", bandwidth=0)

        print(f" \n e: {model_panel_e.f_pooled}, \n t: {model_panel_t.f_pooled}, \n et: {model_panel_et.f_pooled} \n")

        model_random = RandomEffects(y, X).fit(cov_type="kernel", kernel="bartlett")
        chi2, df, pval = hausman(model_panel_e, model_random)
        print(f"chi2: {chi2}, df: {df}, pval: {pval}")

if __name__ == "__main__":
    run_figure2b(save="2b", justification=True)