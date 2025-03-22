"""DS data source implementation."""

import pandas as pd
from utils.constants import DS
from .base import DataSource

class DSDataSource(DataSource):
    """DS data source implementation."""
    
    def import_data(self):
        """Import DS data from Excel file."""
        self.data = pd.read_excel(self.file_path, sheet_name=0, index_col=0)
        return self.data
    
    def clean_data(self):
        """Clean DS data and format dates."""
        # Filtering (Keeping only last entry of each month) and renaming columns
        self.data.columns = pd.to_datetime(self.data.columns)
        self.data = self.data.loc[:, self.data.columns.to_series().groupby(self.data.columns.to_series().dt.to_period("M")).last()]
        self.data.columns = self.data.columns.to_period("M").end_time.date
        self.data.columns = pd.to_datetime(self.data.columns)

        # Filtering and renaming indices
        self.data.index = [index.split('-')[0] for index in self.data.index]
        self.data = self.data.loc[DS.COUNTRIES]
        self.data.index = [DS.COUNTRY_TO_CODE[index] for index in self.data.index]

        # Replacing data for Indonesia
        for date, value in DS.ID_MODIFICATIONS.items():
            date = pd.to_datetime(date, dayfirst=True).to_period("M").to_timestamp("M")
            self.data.loc["ID", date] = value

        return self.data
