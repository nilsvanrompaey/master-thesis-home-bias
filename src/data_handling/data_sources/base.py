"""Base template class for all data sources."""

import os
import pandas as pd
from abc import ABC, abstractmethod

class DataSource(ABC):
    """Base template class for all data sources."""
    
    dataframe_class = pd.DataFrame

    def __init__(self, file_path=None):
        """Initialize the data source.
        
        Args:
            file_path (str, optional): Path to the raw data file
        """
        self.file_path = file_path
        self.data = None
    
    @abstractmethod
    def import_raw_data(self):
        """Import raw data from source file."""
        pass
    
    @abstractmethod
    def clean_raw_data(self):
        """Clean and process the raw data."""
        pass
    
    def save_data(self, save_path, filename):
        """Save the cleaned data to disk.
        
        Args:
            save_path (str): Directory path to save data
            filename (str): Base filename (without extension)
        """
        os.makedirs(save_path, exist_ok=True)
        self.data.to_parquet(os.path.join(save_path, f"{filename}.parquet"))
    
    def load_data(self, save_path, filename):
        """Load saved data from disk.
        
        Args:
            save_path (str): Directory path where data is saved
            filename (str): Base filename (without extension)
        """
        data = pd.read_parquet(os.path.join(save_path, f"{filename}.parquet"))
        self.data = self.dataframe_class(data)
        return self.data
    
    def filter_data(self, countries=None, period=None):
        if countries is not None:
            self.filter_countries(countries)
        if period is not None:
            self.filter_period(period)
        
    @abstractmethod
    def filter_countries(self, countries):
        pass

    @abstractmethod
    def filter_period(self, period):
        pass