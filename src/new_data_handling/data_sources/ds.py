"""DS data source implementation."""

import numpy as np
import pandas as pd
from utils.constants import DS
from .base import DataSource, DataFrame

class DSDataFrame(DataFrame):
    
    @property
    def _constructor(self):
        return DSDataFrame

    def get_data(self, countries="all", period="all", interval="D"):
        """Get data for specific holders, issuers, and time period."""

        data = self.copy()

        assert interval in ["D", "M"]
        if interval == "M":
            data = data.loc[:, data.columns.to_series().groupby(data.columns.to_series().dt.to_period("M")).last()]
            data.columns = data.columns.to_period("M").end_time

        countries = slice(None) if countries == "all" else countries
        if countries != slice(None):
            countries = [countries] if isinstance(countries, str) else countries
            for i, holder in enumerate(countries):
                if len(holder) != 2:
                    countries[i] = DS.COUNTRY_TO_CODE[holder]
            assert all(holder in data.index.get_level_values("Country") for country in countries), "Holding country does not exist"
            
        period = slice(None) if period == "all" else period
        mask = slice(None)
        if period != slice(None):
            start, end = period
            start = pd.Timestamp(str(start))
            end = pd.Timestamp(str(end))
            mask = (data.columns.year >= start.year) & (data.columns.year <= end.year)
            mask[np.argmax(mask) - 1] = True
            data.columns = pd.to_datetime(data.columns.date)

        return data.loc[countries, mask]


class DSDataSource(DataSource):
    """DS data source implementation."""
    
    dataframe_class = DSDataFrame

    def import_raw_data(self):
        """Import DS data from Excel file."""
        self.raw = pd.read_excel(self.file_path, sheet_name=0, index_col=0)
        self.local_raw = pd.read_excel(self.file_path, sheet_name=1, index_col=0)
        self.exchange_raw = pd.read_excel(self.file_path, sheet_name=2, index_col=0)
        return self.raw
    
    def clean_raw_data(self):
        """Clean DS self.data and format dates.
    
        Args:
            self.data (pd.DataFrame): Raw DS data from import_ds
            
        Returns:
            pd.DataFrame: Cleaned DS data
        """
        
        self.data = self.clean_returns_data()
        self.local = self.clean_local_data()
        self.exchange = self.clean_exchange_data()

        for country in self.exchange.index.intersection(self.local.index):
            exchange_rate = self.exchange.loc[country]
            local_prices = self.local.loc[country]
            usd_prices = local_prices / exchange_rate
            self.data.loc[country] = usd_prices

    def clean_returns_data(self):

        # Copy raw data
        self.data = self.raw.copy()
        # Columns
        self.data.columns = pd.to_datetime(self.data.columns)
        # Indices
        self.data.index = [index.split('-')[0] for index in self.data.index]
        valid_index = [country for country in DS.COUNTRIES if country in self.data.index]
        self.data = self.data.loc[valid_index]
        self.data.index = [DS.COUNTRY_TO_CODE[index] for index in self.data.index]
        self.data.index.name = "Country"

        return self.data

    def clean_local_data(self):
        
        # Copy raw data
        self.local = self.local_raw.copy()
        # Columns
        self.local.columns = pd.to_datetime(self.local.columns)
        # Indices
        self.local.index = [index.split('-')[0] for index in self.local.index]
        self.local = self.local.loc[DS.COUNTRIES]
        self.local.index = [DS.COUNTRY_TO_CODE[index] for index in self.local.index]
        self.local.index.name = "Country"

        return self.local
    
    def clean_exchange_data(self):

        # Copy raw data
        self.exchange = self.exchange_raw.copy()
        # Columns
        self.exchange.columns = pd.to_datetime(self.exchange.columns)
        # Indices
        self.exchange.index = [index.split(" ")[0] for index in self.exchange.index]
        self.exchange.index = [DS.EXCHANGE_RATES[index] for index in self.exchange.index]
        self.local.index.name = "Country"

        return self.exchange