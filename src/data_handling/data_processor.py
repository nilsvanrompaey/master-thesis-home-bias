import os

import numpy as np
import pandas as pd

from .data_sources import CPISDataSource, DSDataSource, FEDDataSource, WFEDataSource, WBDataSource, GDPDataSource
from .data_manager import DataManager
from utils import annual_to_monthly_return

def compute_weights(cpis, wb, major, offshore):
    foreign_investments = cpis
    domestic_investments = compute_domestic_investments(cpis, wb, major)
    investments = pd.concat([foreign_investments, domestic_investments])
    investments = investments.groupby(level=list(range(investments.index.nlevels))).sum()
    weights = reallocate_offshore_investments(investments, major, offshore)

    return weights

def compute_domestic_investments(cpis, wb, major):
    total_market_capitalisation = wb.get_data(countries=major).loc[major]
    total_inward_investments = cpis.get_data(issuers=major, holders="WR").droplevel(0).rename_axis("Country")
    total_outward_investments = cpis.get_data(holders=major, issuers="WR").droplevel(1)
    domestic_investments = total_market_capitalisation - total_inward_investments
    domestic_investments.index = pd.MultiIndex.from_arrays([domestic_investments.index, domestic_investments.index], names=["Country", "Counterpart Country"])
    return domestic_investments

def reallocate_offshore_investments(investments, major, offshore):
    sample = major + offshore
    investments = investments.get_data(issuers=sample, holders=sample)
    result = pd.DataFrame(index=pd.MultiIndex.from_product([major,major], names=["Country", "Counterpart Country"]), columns=investments.columns)
    for year in investments.columns:
        S = investments.get_data(issuers=sample, holders=sample, periods=year).unstack(level="Country")
        S.columns = S.columns.droplevel(0)
        offshore_to_drop = list(set(offshore) & set(S.columns[S.sum(axis=0)==0].tolist()))
        offshore_to_keep = list(set(offshore) - set(offshore_to_drop))
        S = S.drop(index=offshore_to_drop).drop(columns=offshore_to_drop)
        S[S<0] = 0
        W = (S / S.sum(axis=0)).fillna(0)
        W_12 = W.loc[major, offshore_to_keep]
        W_21 = W.loc[offshore_to_keep, major]
        W_11 = W.loc[major, major]
        W_22 = W.loc[offshore_to_keep, offshore_to_keep]
        W_ = W_11 + ( W_12.to_numpy() @ np.linalg.inv(np.eye(len(W_22))-W_22.to_numpy())  @ W_21.to_numpy() )
        W_ = W_.stack().swaplevel(0,1).sort_index()
        result[year] = W_

    return result

def compute_index_excess_returns(ds, fed, major):
    returns = ds.loc[major].pct_change(axis=1, fill_method=None).iloc[:,1:]
    riskfree_rate = annual_to_monthly_return(fed.iloc[0])
    excess_returns = returns - riskfree_rate 
    return excess_returns

def compute_excess_returns_statistics(index_excess_returns, weights):
    return_statistics = {}
    
    mean_index_excess_returns = index_excess_returns.mean(axis=1)
    var_index_excess_returns = index_excess_returns.var(axis=1)
    
    mean_portfolio_excess_returns =  mean_index_excess_returns @ weights
    var_portfolio_excess_returns = var_index_excess_returns @ weights
    
    cov_index_portfolio = (index_excess_returns.T.cov() @ weights).values.diagonal()
    cov_index_portfolio = pd.Series(cov_index_portfolio, index=weights.columns)

    return_statistics["mean_index"] = mean_index_excess_returns
    return_statistics["var_index"] = var_index_excess_returns
    return_statistics["mean_portfolio"] = mean_portfolio_excess_returns
    return_statistics["var_portfolio"] = var_portfolio_excess_returns
    return_statistics["cov_index_portfolio"] = cov_index_portfolio

    return return_statistics

# def distribute_offshore_holdings(offshore_investments, offshore_weights):
#     """Distribute offshore holdings based on investments and weights."""
#     offshore_distribution = CPISDataFrame(0.0, index=self.index, columns=self.columns)
#     for year in offshore_investments.columns:
#         investments = offshore_investments.loc[:, year].unstack(level="Counterpart Country")
#         weights = offshore_weights.loc[:, year].unstack(level="Counterpart Country").fillna(0)
#         distribution = investments.dot(weights).stack(level="Counterpart Country")
#         offshore_distribution[year] = distribution
        
#     offshore_distribution.fillna(0, inplace=True)
#     return offshore_distribution

# def calculate_domestic_investments(sample_codes, wb):
#     """Calculate domestic investments for a sample of countries."""
#     total_market_cap = wb.loc[sample_codes, range(2001, 2005)]
#     total_in_sample = self.get_data(issuers=sample_codes, holders="World", periods=range(2001, 2005)).groupby("Counterpart Country").sum()
    
#     total_in_sample.rename_axis("Country", inplace=True)
#     domestic_investments_temp = total_market_cap - total_in_sample
#     domestic_investments = CPISDataFrame(0.0, index=self.index, columns=self.columns)
#     for country, row in domestic_investments_temp.iterrows():
#         domestic_investments.loc[(country, country), range(2001, 2005)] = row.to_numpy()
    
#     return domestic_investments

# def calculate_weight_matrix(wb, sample_period):
#     """Calculate weight matrix for a sample period."""
#     # Get size of country j"s index in country i"s portfolio
#     offshore = [CPIS.COUNTRY_TO_CODE[country] for country in CPIS.OFFSHORE_CENTERS]
#     sample = DS.CODES.copy()
#     offshore_weights = self.calculate_offshore_weights(DS.CODES.copy(), offshore)
#     offshore_investments = self.calculate_offshore_investments(DS.CODES.copy(), offshore)
#     offshore_distribution = self.distribute_offshore_holdings(offshore_investments, offshore_weights)  
#     domestic_investments = self.calculate_domestic_investments(DS.CODES.copy(), wb)
#     size_of_index_in_portfolio = (self + offshore_distribution + domestic_investments).get_data(issuers=sample, holders=sample)
    
#     # Get total size of country i"s portfolio
#     total_portfolio_size = size_of_index_in_portfolio.groupby("Country Name").sum()

#     # Get weights of country j"s index in country i"s portfolio
#     weights = size_of_index_in_portfolio / total_portfolio_size
#     start, end = sample_period
#     weights = weights.get_data(holders=DS.CODES.copy(), periods=range(start, end+1)).mean(axis=1)
    
#     return weights.unstack().T.to_numpy()

# def calculate_excess_returns_matrix(fed, ds, sample_period, log):
#     """Calculate excess returns matrix for a sample period."""
#     # Get time series data [NxT] and filter sample countries and period
#     start, end = sample_period
#     ds = ds.loc[:, (ds.columns >= pd.Timestamp(f"{start-1}-12-01")) & (ds.columns <= pd.Timestamp(f"{end+1}-01-01"))]
#     ds = ds.rename(columns=DS.COUNTRY_TO_CODE, index=DS.COUNTRY_TO_CODE)
#     ds_filled = ds.ffill(axis=1)
#     returns = ds_filled.pct_change(axis=1)

#     # Riskfree rate
#     fed = fed.reindex(columns=ds.columns)
#     fed = annual_to_monthly_return(fed)
#     risk_free_rate = fed.loc["DTB3"]

#     # Convert prices to (log) returns
#     if log: 
#         log_returns = np.log(1 + returns)
#         log_risk_free = np.log(1 + risk_free_rate)
#         excess_returns = log_returns.subtract(log_risk_free, axis=1)
#     else:
#         excess_returns = returns.subtract(risk_free_rate, axis=1)

#     return excess_returns.iloc[:, 1:]

# def calculate_cov_matrix_returns(fed, ds, sample_period, log):
#     """Calculate covariance matrix of returns for a sample period."""
#     # Get returns matrix [NxT]
#     X = self.calculate_excess_returns_matrix(fed, ds, sample_period, log)
    
#     # Return covariance matrix of returns [NxN]
#     return np.cov(X)

# def calculate_cov_index_portfolio(wb, fed, ds, sample_period, log):
#     """Calculate covariance between country"s portfolio and its index."""
#     # Get weight matrix [NxN]
#     W = self.calculate_weight_matrix(wb, sample_period)

#     # Get covariance matrix of returns [NxN]
#     K = self.calculate_cov_matrix_returns(fed, ds, sample_period, log)

#     # Return vector of covariances between country i"s portfolio and its index [1xN]
#     return np.diag(np.dot(W.T, K))
