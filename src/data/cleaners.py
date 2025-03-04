"""Functions for cleaning and processing imported data."""

import pandas as pd
from utils.constants import CPIS, DS

def clean_cpis(data):
    """Clean CPIS data and organize by country.
    
    Args:
        data (pd.DataFrame): Raw CPIS data from import_cpis
        
    Returns:
        dict: Dictionary of cleaned DataFrames by country
    """
    data = data[list(CPIS.COLUMN_HEADERS.keys()) + ["Counterpart Country Name", "Country Name"]]

    pairs = [(holder, issuer) for holder in CPIS.COUNTRIES for issuer in CPIS.COUNTRIES]
    data = (data
            .set_index(["Country Name", "Counterpart Country Name"])
            .groupby(["Country Name", "Counterpart Country Name"]).sum()
            .apply(pd.to_numeric, errors='coerce')
            .fillna(0)            
            .rename(columns=CPIS.COLUMN_HEADERS)
            .reindex(pairs, axis=0, fill_value=0)
            .sort_index()
    )

    return data

def clean_ds(data):
    """Clean DS data and format dates.
    
    Args:
        data (pd.DataFrame): Raw DS data from import_ds
        
    Returns:
        pd.DataFrame: Cleaned DS data
    """
    data = data.copy()
    data.columns = pd.to_datetime(data.columns).date
    data.index = [label.split('-')[0] for label in data.index]
    data = data.loc[DS.COUNTRIES]

    # Keep only the last day of each month
    data.columns = pd.to_datetime(data.columns)
    data = data.loc[:, data.columns.to_series().groupby(data.columns.to_series().dt.to_period("M")).last()]
    data.columns = data.columns.to_period("M").end_time
    return data

def clean_fed(data):
    """Clean FED data and transpose with date formatting.
    
    Args:
        data (pd.DataFrame): Raw FED data from import_fed
        
    Returns:
        pd.DataFrame: Cleaned FED data
    """
    return (data
           .rename(columns={"observation_date": "DATE"})
           .set_index("DATE")
           .transpose()
           .rename(columns=lambda col: pd.to_datetime(col).to_period("M").end_time)
           /100
    )

def clean_wfe(data):
    """Clean WFE data.
    
    Args:
        data (pd.DataFrame): Raw WFE data from import_wfe
        
    Returns:
        pd.DataFrame: Cleaned WFE data
    """
    data.index.set_names(['Code', 'Exchange'], inplace=True)
    return data

def clean_wb(data):
    """Clean WB data.
    
    Args:
        data (pd.DataFrame): Raw WB data from import_wb
        
    Returns:
        pd.DataFrame: Cleaned WB data
    """
    data = data.drop(columns=["Country Code", "Series Name", "Series Code"])
    data.index.set_names(['Country Name'], inplace=True)
    data = data.apply(pd.to_numeric, errors='coerce')  
    data.columns = range(1999,2024)

    return data