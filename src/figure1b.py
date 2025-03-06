import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import numpy as np
from data.manager import *
from utils import *

codes_to_drop = ["UK"]
# codes_to_drop = []

data = DataManager(
    raw_dir = "./data/raw",
    save_dir = "./data/clean"
)
data.load_data()
ds = data.get_dataset("ds").drop([DS.CODE_TO_COUNTRY[code] for code in codes_to_drop])
fed = data.get_dataset("fed")
cpis = data.get_dataset("cpis")


offshore = [CPIS.COUNTRY_TO_CODE[country] for country in CPIS.OFFSHORE_CENTERS]
sample = DS.CODES.copy()
offshore_weights = cpis.calculate_offshore_weights(DS.CODES.copy(), offshore)
offshore_investments = cpis.calculate_offshore_investments(DS.CODES.copy(), offshore)
offshore_distribution = cpis.distribute_offshore_holdings(offshore_investments, offshore_weights)  
domestic_investments = cpis.calculate_domestic_investments(DS.CODES.copy(), wb)
cpis_redis = (cpis + offshore_distribution + domestic_investments).get_data(issuers=sample, holders=sample)
cpis_redis_tot_per_country = cpis_redis.groupby("Country Name").sum()
cpis_redis_weight = cpis_redis / cpis_redis_tot_per_country
first_2001_column = ds.columns[ds.columns.year == 2001].min()
index_of_first_2001 = ds.columns.get_loc(first_2001_column)
ds.loc["ID"].iloc[index_of_first_2001:index_of_first_2001+49] = list(DS.ID_MODIFICATIONS.values())
ds_2004 = ds.loc[:, (ds.columns >= pd.Timestamp("2003-12-01")) & (ds.columns <= pd.Timestamp("2005-01-01"))]
ds_2004 = ds_2004.rename(columns=DS.COUNTRY_TO_CODE, index=DS.COUNTRY_TO_CODE)
cov_2004 = ds_2004.T.cov()
cov_2004
weights = cpis_redis_weight.get_data(holders=sample, periods=2004)
weights_np = weights.unstack().to_numpy()
weights_np
ds_2004_np = ds_2004.pct_change(axis=1).iloc[:, 1:].to_numpy()
cov_2004 = np.cov(ds_2004_np)
cov_2004[0,:] @ weights_np[0,:]
np.diagonal(np.dot(weights_np,cov_2004.T))
var_cov_2004 = pd.DataFrame({"var":ds_2004_np.var(axis=1), "cov":np.diagonal(np.dot(weights_np,cov_2004.T))}, index=ds_2004.index)
var_cov_2004