"""CPIS data source implementation."""

import numpy as np
import pandas as pd

from utils import *
from .base import DataSource

class CPISDataFrame(pd.DataFrame):
    """Specialized DataFrame for CPIS data with additional methods."""
    
    @property
    def _constructor(self):
        return CPISDataFrame

    def get_data(self, holders="all", issuers="all", periods="all"):
        """Get data for specific holders, issuers, and time periods."""
        # Validate and set default parameters
        holders = slice(None) if holders == "all" else holders
        if holders != slice(None):
            holders = [holders] if isinstance(holders, str) else holders
            for i, holder in enumerate(holders):
                if len(holder) != 2:
                    holders[i] = CPIS.COUNTRY_TO_CODE[holder]
            assert all(holder in self.index.get_level_values("Country") for holder in holders), "Holding country does not exist"
            
        issuers = slice(None) if issuers == "all" else issuers
        if issuers != slice(None):
            issuers = [issuers] if isinstance(issuers, str) else issuers
            for i, issuer in enumerate(issuers):
                if len(issuer) != 2:
                    issuers[i] = CPIS.COUNTRY_TO_CODE[issuer]
            assert all(issuer in self.index.get_level_values("Counterpart Country") for issuer in issuers), "Issuer country does not exist"
            
        periods = slice(None) if periods == "all" else periods
        if periods != slice(None):
            periods = [periods] if isinstance(periods, int) else periods
            assert all(period in self.columns for period in periods), "Period does not exist"  

        return self.loc[(holders, issuers), periods]
    
    def calculate_offshore_investments(self, sample, offshore):
        """Calculate offshore investments for a sample of countries."""
        offshore_investments = self.get_data(issuers=offshore, holders=sample)
        return offshore_investments

    def calculate_offshore_weights(self, sample, offshore):
        """Calculate offshore weights for a sample of countries."""
        offshore_in_sample = self.get_data(issuers=sample, holders=offshore)
        offshore_in_sample_sum = offshore_in_sample.groupby(level='Country').sum()
        offshore_weights = (offshore_in_sample / offshore_in_sample_sum)
        return offshore_weights

    def distribute_offshore_holdings(self, offshore_investments, offshore_weights):
        """Distribute offshore holdings based on investments and weights."""
        offshore_distribution = CPISDataFrame(0.0, index=self.index, columns=self.columns)
        for year in offshore_investments.columns:
            investments = offshore_investments.loc[:, year].unstack(level='Counterpart Country')
            weights = offshore_weights.loc[:, year].unstack(level='Counterpart Country').fillna(0)
            distribution = investments.dot(weights).stack(level="Counterpart Country")
            offshore_distribution[year] = distribution
            
        offshore_distribution.fillna(0, inplace=True)
        return offshore_distribution
    
    def calculate_domestic_investments(self, sample_codes, wb):
        """Calculate domestic investments for a sample of countries."""
        total_market_cap = wb.loc[sample_codes, range(2001, 2005)]
        total_in_sample = self.get_data(issuers=sample_codes, holders="World", periods=range(2001, 2005)).groupby("Counterpart Country").sum()
        
        total_in_sample.rename_axis("Country", inplace=True)
        domestic_investments_temp = total_market_cap - total_in_sample
        domestic_investments = CPISDataFrame(0.0, index=self.index, columns=self.columns)
        for country, row in domestic_investments_temp.iterrows():
            domestic_investments.loc[(country, country), range(2001, 2005)] = row.to_numpy()
        
        return domestic_investments
    
    def calculate_weight_matrix(self, wb, sample_period):
        """Calculate weight matrix for a sample period."""
        # Get size of country j's index in country i's portfolio
        offshore = [CPIS.COUNTRY_TO_CODE[country] for country in CPIS.OFFSHORE_CENTERS]
        sample = DS.CODES.copy()
        offshore_weights = self.calculate_offshore_weights(DS.CODES.copy(), offshore)
        offshore_investments = self.calculate_offshore_investments(DS.CODES.copy(), offshore)
        offshore_distribution = self.distribute_offshore_holdings(offshore_investments, offshore_weights)  
        domestic_investments = self.calculate_domestic_investments(DS.CODES.copy(), wb)
        size_of_index_in_portfolio = (self + offshore_distribution + domestic_investments).get_data(issuers=sample, holders=sample)
        
        # Get total size of country i's portfolio
        total_portfolio_size = size_of_index_in_portfolio.groupby("Country Name").sum()

        # Get weights of country j's index in country i's portfolio
        weights = size_of_index_in_portfolio / total_portfolio_size
        start, end = sample_period
        weights = weights.get_data(holders=DS.CODES.copy(), periods=range(start, end+1)).mean(axis=1)
        
        return weights.unstack().T.to_numpy()
    
    def calculate_excess_returns_matrix(self, fed, ds, sample_period, log):
        """Calculate excess returns matrix for a sample period."""
        # Get time series data [NxT] and filter sample countries and period
        start, end = sample_period
        ds = ds.loc[:, (ds.columns >= pd.Timestamp(f"{start-1}-12-01")) & (ds.columns <= pd.Timestamp(f"{end+1}-01-01"))]
        ds = ds.rename(columns=DS.COUNTRY_TO_CODE, index=DS.COUNTRY_TO_CODE)
        ds_filled = ds.ffill(axis=1)
        returns = ds_filled.pct_change(axis=1)

        # Riskfree rate
        fed = fed.reindex(columns=ds.columns)
        fed = annual_to_monthly_return(fed)
        risk_free_rate = fed.loc["DTB3"]

        # Convert prices to (log) returns
        if log: 
            log_returns = np.log(1 + returns)
            log_risk_free = np.log(1 + risk_free_rate)
            excess_returns = log_returns.subtract(log_risk_free, axis=1)
        else:
            excess_returns = returns.subtract(risk_free_rate, axis=1)

        return excess_returns.iloc[:, 1:]

    def calculate_cov_matrix_returns(self, fed, ds, sample_period, log):
        """Calculate covariance matrix of returns for a sample period."""
        # Get returns matrix [NxT]
        X = self.calculate_excess_returns_matrix(fed, ds, sample_period, log)
        
        # Return covariance matrix of returns [NxN]
        return np.cov(X)
    
    def calculate_cov_index_portfolio(self, wb, fed, ds, sample_period, log):
        """Calculate covariance between country's portfolio and its index."""
        # Get weight matrix [NxN]
        W = self.calculate_weight_matrix(wb, sample_period)

        # Get covariance matrix of returns [NxN]
        K = self.calculate_cov_matrix_returns(fed, ds, sample_period, log)

        # Return vector of covariances between country i's portfolio and its index [1xN]
        return np.diag(np.dot(W.T, K))


class CPISDataSource(DataSource):
    """CPIS data source implementation."""
    
    dataframe_class = CPISDataFrame

    def import_raw_data(self):
        """Import CPIS data from CSV file."""
        self.raw = pd.read_csv(self.file_path, low_memory=False)
        return self.raw
        
    def clean_raw_data(self):
        """Clean CPIS data and organize by country."""
        
        self.data = self.raw

        # Setting indices, removing duplicate indices and filling NaN
        self.data = self.data.set_index(["Country Name", "Counterpart Country Name"])
        self.data = self.data.rename_axis(["Country", "Counterpart Country"])
        self.data = self.data.groupby(["Country", "Counterpart Country"]).sum()
        self.data = self.data.apply(pd.to_numeric, errors='coerce').fillna(0)

        # Filtering (remove half-yearly, retain yearly) and renaming columns
        self.data = self.data[list(CPIS.COLUMN_HEADERS.keys())]
        self.data = self.data.rename(columns=CPIS.COLUMN_HEADERS)

        # Filtering and renaming indices
        pairs = [(holder, issuer) for holder in CPIS.COUNTRIES for issuer in CPIS.COUNTRIES]    
        self.data = self.data.reindex(pairs, axis=0, fill_value=0)
        self.data = self.data.rename(index=CPIS.COUNTRY_TO_CODE)
        self.data = self.data.sort_index()

        return self.data

    def filter_countries(self, countries):
        pairs = [(holder, issuer) for holder in countries for issuer in countries]
        self.data = self.data.reindex(pairs, axis=0, fill_value=0)
        self.data = self.data.sort_index()
        return self.data

    def filter_period(self, period):
        start, end = period
        if start is None:
            start = min(self.data.columns)
        if end is None:
            end = max(self.data.columns)
        self.data = self.data[range(start, end+1)]
        return self.data

