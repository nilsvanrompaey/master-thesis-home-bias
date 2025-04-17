"""Main data manager class to orchestrate all data sources."""

import os
from .data_sources import CPISDataSource, DSDataSource, FEDDataSource, WFEDataSource, WBDataSource, GDPDataSource

class DataManager:
    """Manages all data sources and orchestrates the data pipeline."""
    
    def __init__(self, raw_dir, save_dir):
        """Initialize the DataManager.
        
        Args:
            raw_dir (str): Directory path containing raw data files
            save_dir (str): Directory path to save processed data
        """
        self.raw_dir = raw_dir
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        
        # Initialize data sources
        self.sources = {
            "cpis": CPISDataSource(os.path.join(raw_dir, "CPIS.csv")),
            "ds": DSDataSource(os.path.join(raw_dir, "DS.xlsx")),
            "fed": FEDDataSource(os.path.join(raw_dir, "DTB3.xlsx")),
            "wb": WBDataSource(os.path.join(raw_dir, "WB.xlsx")),
            "wfe": WFEDataSource(os.path.join(raw_dir, "WFE.xlsx")),
            "gdp": GDPDataSource(os.path.join(raw_dir, "GDP.xlsx")),
        }
        
        # Load the cleaned data (from parquet files)    
        try:
            self.load_data()
        except Exception:
            self.clean_data()
            self.save_data()
    
    def clean_data(self, names=None):
        """Import and clean all datasets."""
        names = self.sources.keys() if names is None else names
        for name, source in self.sources.items():
            if name in names:
                source.import_raw_data()
                source.clean_raw_data()

    def save_data(self):
        """Save all loaded datasets."""
        for name, source in self.sources.items():
            source.save_data(self.save_dir, name)
        self.load_data()

    def load_data(self):
        """Load all saved datasets."""
        for name, source in self.sources.items():
            source.load_data(self.save_dir, name)
            self.__setattr__(name, self.sources[name].data)

    def get_dataset(self, name):
        """Retrieve a dataset."""
        if name in self.sources:
            return self.sources[name].data
        return None        