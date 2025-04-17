"""GDP data source implementation."""

import numpy as np
import pandas as pd

from utils import *
from .base import DataSource

class GDPDataFrame(pd.DataFrame):
    
    @property
    def _constructor(self):
        return GDPDataFrame

    def get_data(self, countries="all", period="all", gdp_type="gdp"):
        
        data = self.copy()

        countries = slice(None) if countries == "all" else countries
        if countries != slice(None):
            countries = [countries] if isinstance(countries, str) else countries
            for i, holder in enumerate(countries):
                if len(holder) != 2:
                    countries[i] = CPIS.COUNTRY_TO_CODE[holder]
            assert all(holder in data.index.get_level_values("Country") for holder in countries), "Holding country does not exist"
                       
        if period == "all":
            mask = slice(None)
        else:
            start, end = period
            start = pd.Timestamp(str(start))
            end = pd.Timestamp(str(end))
            columns = pd.Series([pd.Timestamp(str(column)) for column in data.columns], index=data.columns)
            mask = (columns >= start) & (columns <= end)

        assert gdp_type in data.index.get_level_values(0)
        data = data.loc[(slice(None), countries), mask]

        return data.loc[gdp_type]
    
class GDPDataSource(DataSource):
    """CPIS data source implementation."""
    
    dataframe_class = GDPDataFrame

    def import_raw_data(self):
        """Import GDP data from excel file."""
        self.raw = {}
        self.raw["gdp"] = pd.read_excel(self.file_path, index_col=1, sheet_name=0)
        self.raw["gdp_cap"] = pd.read_excel(self.file_path, index_col=1, sheet_name=1)
        self.raw["gdp_ppp"] = pd.read_excel(self.file_path, index_col=1, sheet_name=2)
        self.raw["gdp_cap_ppp"] = pd.read_excel(self.file_path, index_col=1, sheet_name=3)

        return self.raw
        
    def clean_raw_data(self):
        """Clean GDP data and organize by country."""
        
        gdp_types = list(self.raw.keys())
        data_dict = {}  
        for gdp_type in gdp_types:
            data = self.raw[gdp_type]
            data = data.drop(data.columns[[0, 1, 2]], axis=1)
            data.index.name = "Country"
            data.columns = data.columns.str.split("[").str[0].astype(int)
            data = data.rename(index=WB.CODES_3_TO_2)
            data = data.loc[data.index.isin(DS.CODES)]
            data_dict[gdp_type] = data.apply(pd.to_numeric, errors='coerce')

        index = pd.MultiIndex.from_product([gdp_types, data_dict[gdp_type].index], names=["GDP type", "Country"])
        columns = data_dict[gdp_type].columns
        self.data = pd.DataFrame(index=index, columns=columns)
        for gdp_type in gdp_types:
            data = data_dict[gdp_type]
            data.index = pd.MultiIndex.from_product([[gdp_type], data.index])
            self.data.loc[gdp_type] = data

        return self.data