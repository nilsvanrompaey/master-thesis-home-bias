"""WB data source implementation."""

import pandas as pd
from utils.constants import WB, WFE
from .base import DataSource

class WBDataSource(DataSource):
    """WB data source implementation."""
    
    def import_raw_data(self):
        """Import WB data from Excel file."""
        self.raw = pd.read_excel(self.file_path, sheet_name=0, usecols="A:AC", index_col=1)
        return self.raw
    
    def clean_raw_data(self):
        """Clean WB data."""

        self.data = self.raw

        self.data = self.data.drop(columns=["Country Name", "Series Name", "Series Code"])
        self.data.index = [WB.CODES_3_TO_2.get(index, "NaN") for index in self.data.index.tolist()]
        self.data = self.data.loc[self.data.index != "NaN"]
        self.data = self.data.rename_axis("Country Code")
        self.data = self.data.apply(pd.to_numeric, errors='coerce')  
        self.data.columns = range(1999, 2024)
        self.data.index.name = "Country"

        for country, country_data in WFE.WFE_MODIFICATIONS.items():
            for year, value in country_data.items():
                self.data.loc[country, year] = value

        return self.data
    
    def filter_countries(self, countries):
        self.data = self.data.reindex(countries, axis=0, fill_value=0)
        self.data = self.data.sort_index()
        return self.data

    def filter_period(self, period):
        start, end = period
        self.data = self.data[range(start, end+1)]
        return self.data