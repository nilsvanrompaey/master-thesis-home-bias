"""Functions for importing raw data from various sources."""

import pandas as pd

def import_cpis(file_path):
    """Import CPIS data from CSV file.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pd.DataFrame: Raw CPIS data
    """
    return pd.read_csv(file_path)

def import_cpis_single(file_path):
    """Import single CPIS data from Excel file.
    
    Args:
        file_path (str): Path to the Excel file
        
    Returns:
        pd.DataFrame: Raw CPIS single data
    """
    return pd.read_excel(file_path, sheet_name=0, usecols="B:AJ", skiprows=4, index_col=0)[:-5]

def import_ds(file_path):
    """Import DS data from Excel file.
    
    Args:
        file_path (str): Path to the Excel file
        
    Returns:
        pd.DataFrame: Raw DS data
    """
    return pd.read_excel(file_path, sheet_name=0, index_col=0)

def import_fed(file_path):
    """Import FED data from Excel file.
    
    Args:
        file_path (str): Path to the Excel file
        
    Returns:
        pd.DataFrame: Raw FED data
    """
    return pd.read_excel(file_path, sheet_name=1)

def import_wfe(file_path):
    """Import WFE data from Excel file.
    
    Args:
        file_path (str): Path to the Excel file
        
    Returns:
        pd.DataFrame: Raw WFE data
    """
    return pd.read_excel(file_path, sheet_name=1, usecols="A:AC", skiprows=3, index_col=0)

def import_wb(file_path):
    """Import WB data from Excel file.

    Args:
        file_path (str): Path to the Excel file
        
    Returns:
        pd.DataFrame: Raw WB data
    """
    return pd.read_excel(file_path, sheet_name=0, usecols="A:AC", index_col=1)