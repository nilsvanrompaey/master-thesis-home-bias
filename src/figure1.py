import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import numpy as np
from data_handling import *
from utils import *
from adjustText import adjust_text
from plot.plot import scatter_countries
from data_handling.data_processor import *

dm = DataManager(
    raw_dir = "./data/raw",
    save_dir = "./data/clean"
)

dm.load_data()

# period = (2001,2004)
# dm.filter_data(None, period)

ds = dm.get_dataset("ds")
fed = dm.get_dataset("fed")
cpis = dm.get_dataset("cpis")
wb = dm.get_dataset("wb")

major = COUNTRIES.MAJOR
offshore = COUNTRIES.OFFSHORE
sample = major + offshore

index_excess_returns = compute_index_excess_returns(ds, fed, major)
weights = compute_weights(cpis, wb, major, offshore).mean(axis=1).unstack(level="Country")
# weights = compute_weights(cpis, wb, major, offshore)[2004].unstack(level="Country")

return_statistics = compute_excess_returns_statistics(index_excess_returns, weights)

var_excess = return_statistics["var_index"]
mean_excess = return_statistics["mean_index"]
cov_excess = return_statistics["cov_index_portfolio"]

avg_riskfree_rate = annual_to_monthly_return(fed).mean(axis=1).iloc[0]

def run_figure1(codes, save_name):

	fig, axes = plt.subplots(1, 2, figsize=(10, 4))
	scatter_countries(ax=axes[0],
					x=var_excess,
					y=mean_excess,
					codes=codes,
					x_label="Variance of excess returns",
					y_label="Mean excess return",
					#   title="Monthly excess returns (USD)",
					save=f"exp1/results/fig1a{save_name}",
					riskfree=avg_riskfree_rate,
					)
	scatter_countries(ax=axes[1],
					x=cov_excess,
					y=mean_excess,
					codes=codes,
					x_label="Covariance between excess returns of index and portfolio",
					y_label="Mean excess return",
					#   title="Monthly excess returns (USD)",
					save=f"exp1/results/fig1b{save_name}",           
					riskfree=avg_riskfree_rate,
					)
	plt.suptitle("Monthly excess returns 2001-2004 (USD)")
	plt.tight_layout()
	plt.savefig(f"./output/exp1/figures/fig1{save_name}.pdf", dpi=600)

if __name__ == "__main__":
	codes = COUNTRIES.MAJOR
	run_figure1(codes=codes, save_name="")
	# codes.remove("TR")
	# run_figure1(codes=codes, save_name="_exTR")