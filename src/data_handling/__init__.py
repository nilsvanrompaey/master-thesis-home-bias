"""Package initialization file."""

from .data_manager import DataManager
from .data_sources import (
    DataSource,
    CPISDataSource,
    DSDataSource, 
    FEDDataSource,
    WFEDataSource,
    WBDataSource,
    CPISDataFrame
)

__all__ = [
    # Core classes
    "DataManager",
    
    # Data source classes
    "DataSource",
    "CPISDataSource",
    "DSDataSource",
    "FEDDataSource",
    "WFEDataSource",
    "WBDataSource",
    
    # Specialized data classes
    "CPISDataFrame",
]
