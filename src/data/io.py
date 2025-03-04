"""Classes for saving and loading data."""

import os
import pandas as pd

class DataSaver:
    """Handles saving cleaned data for future use."""
    
    def __init__(self, save_path):
        """Initialize the DataSaver.
        
        Args:
            save_path (str): Directory path to save data
        """
        self.save_path = save_path
        os.makedirs(save_path, exist_ok=True)

    def save_dataframe(self, df, filename):
        """Save a DataFrame to parquet format.
        
        Args:
            df (pd.DataFrame): DataFrame to save
            filename (str): Base filename (without extension)
        """
        df.to_parquet(os.path.join(self.save_path, f"{filename}.parquet"))


class DataLoader:
    """Loads saved, cleaned data from disk."""
    
    def __init__(self, save_path):
        """Initialize the DataLoader.
        
        Args:
            save_path (str): Directory path where data is saved
        """
        self.save_path = save_path

    def load_dataframe(self, filename):
        """Load a DataFrame from a parquet file.
        
        Args:
            filename (str): Base filename (without extension)
            
        Returns:
            pd.DataFrame: Loaded DataFrame
        """
        return pd.read_parquet(os.path.join(self.save_path, f"{filename}.parquet"))