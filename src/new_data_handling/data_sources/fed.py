"""FED data source implementation."""

import numpy as np
import pandas as pd

from utils import *
from .base import DataSource, DataFrame

class FEDDataFrame(DataFrame):

    @property
    def _constructor(self):
        return FEDDataFrame
    
    def get_data(self, period="all", compounding="Y"):
        
        data = self.copy()

        assert (period=="all" or isinstance(period, tuple))
        if period == "all":
            mask = slice(None)
        else:
            start, end = period
            start = pd.Timestamp(str(start))
            end = pd.Timestamp(str(end))
            mask = (data.columns.year >= start.year) & (data.columns.year <= end.year)
        data = data.loc[:,mask]

        assert compounding in ["Y", "M"]
        if compounding == "M":
            data = annual_to_monthly_return(data)

        return data
    
class FEDDataSource(DataSource):
    """FED data source implementation."""
    
    dataframe_class = FEDDataFrame

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