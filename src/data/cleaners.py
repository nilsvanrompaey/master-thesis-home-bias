"""Functions for cleaning and processing imported data."""

import pandas as pd
from utils.constants import CPIS, DS, WB, WFE

def clean_cpis(data):
    """Clean CPIS data and organize by country.
    
    Args:
        data (pd.DataFrame): Raw CPIS data from import_cpis
        
    Returns:
        dict: Dictionary of cleaned DataFrames by country
    """
    # Setting indices, removing duplicate indices and filling NaN
    data = data.set_index(["Country Name", "Counterpart Country Name"])
    data = data.groupby(["Country Name", "Counterpart Country Name"]).sum()
    data = data.apply(pd.to_numeric, errors='coerce').fillna(0)

    # Filtering and renaming columns
    data = data[list(CPIS.COLUMN_HEADERS.keys())]
    data = data.rename(columns=CPIS.COLUMN_HEADERS)

    # Filtering and renaming indices
    pairs = [(holder, issuer) for holder in CPIS.COUNTRIES for issuer in CPIS.COUNTRIES]    
    data = data.reindex(pairs, axis=0, fill_value=0)
    data = data.rename(index=CPIS.COUNTRY_TO_CODE)
    data = data.sort_index()

    return data

def clean_ds(data):
    """Clean DS data and format dates.
    
    Args:
        data (pd.DataFrame): Raw DS data from import_ds
        
    Returns:
        pd.DataFrame: Cleaned DS data
    """
    data = data.copy()
    data.columns = pd.to_datetime(data.columns)
    data.index = [index.split('-')[0] for index in data.index]
    data = data.loc[DS.COUNTRIES]
    data.index = [DS.COUNTRY_TO_CODE[index] for index in data.index]

    # Keep only the last day of each month
    data = data.loc[:, data.columns.to_series().groupby(data.columns.to_series().dt.to_period("M")).last()]
    data.columns = data.columns.to_period("M").end_time.date
    data.columns = pd.to_datetime(data.columns)
    return data

def clean_fed(data):
    """Clean FED data and transpose with date formatting.
    
    Args:
        data (pd.DataFrame): Raw FED data from import_fed
        
    Returns:
        pd.DataFrame: Cleaned FED data
    """
    data = data.rename(columns={"observation_date": "DATE"}).set_index("DATE")
    data = data.transpose()
    data.columns = data.columns.to_period("M").end_time.date
    data.columns = pd.to_datetime(data.columns)
    return data / 100

def clean_wfe(data):
    """Clean WFE data.
    
    Args:
        data (pd.DataFrame): Raw WFE data from import_wfe
        
    Returns:
        pd.DataFrame: Cleaned WFE data
    """
    data = data.drop(columns=data.columns[0], axis=1)
    data = data.rename_axis(["Code"])
    data = data.groupby(["Code"]).sum()
    data = data.apply(pd.to_numeric, errors='coerce')  
    data.columns = range(1999,2026)

    for country, country_data in WFE.WFE_MODIFICATIONS.items():
        for year, value in country_data.items():
            data.loc[country, year] = value

    return data

def clean_wb(data):
    """Clean WB data.
    
    Args:
        data (pd.DataFrame): Raw WB data from import_wb
        
    Returns:
        pd.DataFrame: Cleaned WB data
    # """
    data = data.drop(columns=["Country Name", "Series Name", "Series Code"])
    data.index = [WB.CODES_3_TO_2.get(index, "NA") for index in data.index.tolist()]
    data = data.rename_axis("Country Code")
    data = data.apply(pd.to_numeric, errors='coerce')  
    data.columns = range(1999,2024)

    for country, country_data in WFE.WFE_MODIFICATIONS.items():
        for year, value in country_data.items():
            data.loc[country, year] = value

    return data