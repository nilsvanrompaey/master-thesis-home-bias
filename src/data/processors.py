import pandas as pd

from utils.constants import CPIS

class DataFrameCPIS(pd.DataFrame):
    @property
    def _constructor(self):
        return DataFrameCPIS

    def get_data(self, holders="all", issuers="all", periods="all"):

        # Validate and set default parameters
        holders = slice(None) if holders == "all" else holders
        if holders != slice(None):
            holders = [holders] if isinstance(holders, str) else holders
            for i, holder in enumerate(holders):
                if len(holder) == 2:
                    holders[i] = CPIS.CODE_TO_COUNTRY[holder]
            assert all(holder in self.index.get_level_values("Country Name") for holder in holders), "Holding country does not exist"
            
        issuers = slice(None) if issuers == "all" else issuers
        if issuers != slice(None):
            issuers = [issuers] if isinstance(issuers, str) else issuers
            for i, issuer in enumerate(issuers):
                if len(issuer) == 2:
                    issuers[i] = CPIS.CODE_TO_COUNTRY[issuer]
            assert all(issuer in self.index.get_level_values("Counterpart Country Name") for issuer in issuers), "Issuer country does not exist"
            
        periods = slice(None) if periods == "all" else periods
        if periods != slice(None):
            periods = [periods] if isinstance(periods, int) else periods
            assert all(period in self.columns for period in periods), "Period does not exist"  

        return self.loc[(holders, issuers), periods]
    
    def calculate_offshore_investments(self, sample, offshore):
        offshore_investments = self.get_data(issuers=offshore, holders=sample)

        return offshore_investments

    def calculate_offshore_weights(self, sample, offshore):
        offshore_in_sample = self.get_data(issuers=sample, holders=offshore)
        offshore_in_sample_sum = offshore_in_sample.groupby(level='Country Name').sum()
        offshore_weights = (offshore_in_sample / offshore_in_sample_sum)

        return offshore_weights

    def distribute_offshore_holdings(self, offshore_investments, offshore_weights):
        offshore_distribution = DataFrameCPIS(0.0, index=self.index, columns=self.columns)
        for year in offshore_investments.columns:
            investments = offshore_investments.loc[:, year].unstack(level='Counterpart Country Name')
            weights = offshore_weights.loc[:, year].unstack(level='Counterpart Country Name').fillna(0)
            distribution = investments.dot(weights).stack(level="Counterpart Country Name")
            offshore_distribution[year] = distribution
            
        offshore_distribution.fillna(0, inplace=True)
        return offshore_distribution
    
    def calculate_domestic_investments(self, sample_codes, wb):
        total_market_cap = wb.loc[sample_codes, range(2001,2005)]
        total_in_sample = self.get_data(issuers=sample_codes, holders="World", periods=range(2001,2005)).groupby("Counterpart Country Name").sum()
        
        total_in_sample.index = [CPIS.COUNTRY_TO_CODE.get(index, "NA") for index in total_in_sample.index.tolist()]
        total_in_sample.rename_axis("Country Code", inplace=True)
        domestic_investments_temp = total_market_cap - total_in_sample
        domestic_investments = DataFrameCPIS(0.0, index=self.index, columns=self.columns)
        for country_code, row in domestic_investments_temp.iterrows():
            country = CPIS.CODE_TO_COUNTRY[country_code]
            domestic_investments.loc[(country, country), range(2001,2005)] = row
        
        return domestic_investments