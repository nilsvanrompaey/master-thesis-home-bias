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
            "gdp": GDPDataSource(os.path.join(raw_dir, "GDP.xlsx"))
        }
        
        #Load or process data
        try:
            self.load_data()
        except Exception:
            self.clean_and_save_data()

    
    def clean_and_save_data(self):
        """Import, clean, and save all datasets."""
        for name, source in self.sources.items():
            source.import_data()
            source.clean_data()
            source.save_data(self.save_dir, name)
        self.load_data()
    
    def load_data(self):
        """Load all saved datasets."""
        for name, source in self.sources.items():
            source.load_data(self.save_dir, name)
    
    def get_dataset(self, name):
        """Retrieve a dataset.
        
        Args:
            name (str): Name of the dataset to retrieve
            
        Returns:
            object: The requested dataset or None if not found
        """
        if name in self.sources:
            return self.sources[name].data
        return None
