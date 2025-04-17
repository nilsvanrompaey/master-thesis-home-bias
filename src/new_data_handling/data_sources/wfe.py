"""WFE data source implementation."""

import pandas as pd
from utils.constants import WFE
from .base import DataSource, DataFrame

class WFEDataFrame(DataFrame):
    
    @property
    def _constructor(self):
        return WFEDataFrame

    def get_data(self, countries="all", period="all"):

        data = self.copy()

        countries = slice(None) if countries == "all" else countries
        if countries != slice(None):
            countries = [countries] if isinstance(countries, str) else countries
            for i, holder in enumerate(countries):
                if len(holder) != 2:
                    countries[i] = WFE.COUNTRY_TO_CODE[holder]
            assert all(holder in self.index.get_level_values("Country") for country in countries), "Holding country does not exist"
        
        if period == "all":
            mask = slice(None)
        else:
            start, end = period
            start = pd.Timestamp(str(start))
            end = pd.Timestamp(str(end))
            columns = pd.Series([pd.Timestamp(str(column)) for column in data.columns], index=data.columns)
            mask = (columns >= start) & (columns <= end)  

        return self.loc[countries, mask]
    

class WFEDataSource(DataSource):
    """WFE data source implementation."""
    
    dataframe_class = WFEDataFrame

    def import_raw_data(self):
        """Import WFE data from Excel file."""
        self.raw = pd.read_excel(self.file_path, sheet_name=1, usecols="A:AC", skiprows=3, index_col=0)
        return self.raw
    
    def clean_raw_data(self):
        """Clean WFE data."""

        self.data = self.raw

        self.data = self.data.drop(columns=self.data.columns[0], axis=1)
        self.data = self.data.rename_axis(["Code"])
        self.data = self.data.groupby(["Code"]).sum()
        self.data = self.data.apply(pd.to_numeric, errors='coerce') * 1e6
        self.data.columns = range(1999, 2026)
        self.data.index.name = "Country"

        for country, country_data in WFE.WFE_MODIFICATIONS.items():
            for year, value in country_data.items():
                self.data.loc[country, year] = value

        return self.data
