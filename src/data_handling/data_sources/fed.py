"""FED data source implementation."""

import pandas as pd
from .base import DataSource

class FEDDataSource(DataSource):
    """FED data source implementation."""
    
    def import_raw_data(self):
        """Import FED data from Excel file."""
        self.raw = pd.read_excel(self.file_path, sheet_name=1)
        return self.raw
    
    def clean_raw_data(self):
        """Clean FED data and transpose with date formatting."""
        
        self.data = self.raw
        
        self.data = self.data.rename(columns={"observation_date": "DATE"}).set_index("DATE")
        self.data = self.data.transpose()
        self.data.columns = self.data.columns.to_period("M").end_time.date
        self.data.columns = pd.to_datetime(self.data.columns)
        self.data = self.data / 100
        return self.data

    def filter_countries(self, countries):
        pass

    def filter_period(self, period):
        start, end = period
        self.data = self.data.loc[:, [year in range(2010,2014) for year in self.data.columns.year]]
        return self.data