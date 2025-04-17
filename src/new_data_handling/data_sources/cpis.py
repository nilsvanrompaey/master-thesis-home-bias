"""CPIS data source implementation."""

import numpy as np
import pandas as pd

from utils import *
from .base import DataSource, DataFrame

class CPISDataFrame(DataFrame):
    """Specialized DataFrame for CPIS data with additional methods."""

    @property
    def _constructor(self):
        return CPISDataFrame

    def get_data(self, countries="all", period="all", counterparts="all"):
        """Get data for specific countries (holders), counterparts (issuers), and time period."""

        data = self.copy()

        countries = slice(None) if countries == "all" else countries
        if countries != slice(None):
            countries = [countries] if isinstance(countries, str) else countries
            for i, country in enumerate(countries):
                if len(country) != 2:
                    countries[i] = CPIS.COUNTRY_TO_CODE[country]
            assert all(country in data.index.get_level_values("Country") for country in countries), "Country does not exist"
            
        counterparts = slice(None) if counterparts == "all" else counterparts
        if counterparts != slice(None):
            counterparts = [counterparts] if isinstance(counterparts, str) else counterparts
            for i, counterpart in enumerate(counterparts):
                if len(counterpart) != 2:
                    counterparts[i] = CPIS.COUNTRY_TO_CODE[counterpart]
            assert all(counterpart in data.index.get_level_values("Counterpart Country") for counterpart in counterparts), "Counterpart country does not exist"
            
        period = slice(None) if period == "all" else period
        mask = slice(None)
        if period != slice(None):
            start, end = period
            start = pd.Timestamp(str(start))
            end = pd.Timestamp(str(end))
            columns = pd.Series([pd.Timestamp(str(column)) for column in data.columns], index=data.columns)
            mask = (columns >= start) & (columns <= end)
        
        return data.loc[(countries, counterparts), mask]
    

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
