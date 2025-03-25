"""WFE data source implementation."""

import pandas as pd
from utils.constants import WFE
from .base import DataSource

class WFEDataSource(DataSource):
    """WFE data source implementation."""
    
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

    def filter_countries(self, countries):
        self.data = self.data.reindex(countries, axis=0, fill_value=0)
        self.data = self.data.sort_index()
        return self.data

    def filter_period(self, period):
        start, end = period
        self.data = self.data[range(start, end+1)]
        return self.data
