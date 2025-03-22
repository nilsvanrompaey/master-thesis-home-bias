"""FED data source implementation."""

import pandas as pd
from .base import DataSource

class FEDDataSource(DataSource):
    """FED data source implementation."""
    
    def import_data(self):
        """Import FED data from Excel file."""
        self.data = pd.read_excel(self.file_path, sheet_name=1)
        return self.data
    
    def clean_data(self):
        """Clean FED data and transpose with date formatting."""
        self.data = self.data.rename(columns={"observation_date": "DATE"}).set_index("DATE")
        self.data = self.data.transpose()
        self.data.columns = self.data.columns.to_period("M").end_time.date
        self.data.columns = pd.to_datetime(self.data.columns)
        self.data = self.data / 100
        return self.data
