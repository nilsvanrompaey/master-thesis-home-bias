"""Main manager class for data handling pipeline."""

from .importers import import_cpis, import_ds, import_fed, import_wfe, import_wb
from .cleaners import clean_cpis, clean_ds, clean_fed, clean_wfe, clean_wb
from .io import DataSaver, DataLoader
from .processors import DataFrameCPIS
from utils.constants import CPIS
import pandas as pd

class DataManager:
    """Manages the entire data handling pipeline."""
    
    def __init__(self, raw_dir, save_dir):
        """Initialize the DataManager.
        
        Args:
            raw_paths (dict): Dictionary of file paths for raw data
            save_path (str): Directory path to save processed data
        """
        self.raw_dir = raw_dir
        self.save_dir = save_dir
        self.saver = DataSaver(save_dir)
        self.loader = DataLoader(save_dir)
        self.datasets = {}
        try:
            self.load_data()
        except Exception:
            self.clean_and_save_data()
        self.load_data()

    def clean_and_save_data(self):
        """Import, clean, and save all datasets."""
        # Import raw data
        raw_data = {
            "cpis": import_cpis(self.raw_dir + "/CPIS.csv"),
            "ds": import_ds(self.raw_dir + "/DS.xlsx"),
            "fed": import_fed(self.raw_dir + "/FED.xlsx"),
            "wb": import_wb(self.raw_dir + "/WB.xlsx"),
            "wfe": import_wfe(self.raw_dir + "/WFE.xlsx"),   
        }
        
        # Clean data
        cleaned_data = {
            "cpis": DataFrameCPIS(clean_cpis(raw_data["cpis"])),
            "ds": clean_ds(raw_data["ds"]),
            "fed": clean_fed(raw_data["fed"]),
            "wb": clean_wb(raw_data["wb"]),
            "wfe": clean_wfe(raw_data["wfe"]),
        }
        
        # Save data
        self.saver.save_dataframe(cleaned_data["cpis"], "cpis")
        self.saver.save_dataframe(cleaned_data["ds"], "ds")
        self.saver.save_dataframe(cleaned_data["fed"], "fed")
        self.saver.save_dataframe(cleaned_data["wb"], "wb")
        self.saver.save_dataframe(cleaned_data["wfe"], "wfe")
        
        # Store in memory
        self.datasets = cleaned_data

    def load_data(self):
        """Load saved datasets into memory."""
        self.datasets = {
            # "cpis": self.loader.load_dataframe("cpis"),
            "cpis": DataFrameCPIS(self.loader.load_dataframe("cpis").transpose()),
            "ds": self.loader.load_dataframe("ds"),
            "fed": self.loader.load_dataframe("fed"),
            "wb": self.loader.load_dataframe("wb"),
            "wfe": self.loader.load_dataframe("wfe"),
        }

    def get_dataset(self, name):
        """Retrieve a dataset from memory.
        
        Args:
            name (str): Name of the dataset to retrieve
            
        Returns:
            object: The requested dataset or None if not found
        """
        return self.datasets.get(name)

