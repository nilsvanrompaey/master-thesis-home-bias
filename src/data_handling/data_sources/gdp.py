"""GDP data source implementation."""

import numpy as np
import pandas as pd

from utils import *
from .base import DataSource

class GDPDataFrame(pd.DataFrame):
    """Specialized DataFrame for CPIS data with additional methods."""
    
    @property
    def _constructor(self):
        return GDPDataFrame

class GDPDataSource(DataSource):
    """CPIS data source implementation."""
    
    dataframe_class = GDPDataFrame

    def import_data(self):
        """Import GDP data from excel file."""
        self.data = pd.read_excel(self.file_path, index_col=1)
        return self.data
        
    def clean_data(self):
        """Clean GDP data and organize by country."""
        self.data = self.data.drop(self.data.columns[[0, 1, 2]], axis=1)
        self.data.index.name = "Country"
        self.data.columns = self.data.columns.str.split("[").str[0].astype(int)
        self.data = self.data.rename(index=WB.CODES_3_TO_2)
        self.data = self.data.loc[self.data.index.isin(DS.CODES)]
        self.data = self.data.apply(pd.to_numeric, errors='coerce')
        
        # Convert to specialized CPIS DataFrame
        return self.data

